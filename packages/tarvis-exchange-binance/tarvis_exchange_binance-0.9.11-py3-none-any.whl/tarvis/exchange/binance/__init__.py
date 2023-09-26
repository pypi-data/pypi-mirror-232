import binance.api  # noqa
from binance.cm_futures import CMFutures  # noqa
from binance.error import ClientError  # noqa
from binance.lib.utils import cleanNoneValue  # noqa
from binance.spot import Spot  # noqa
from binance.um_futures import UMFutures  # noqa
from decimal import Decimal
from enum import Enum
from requests import Response, Session
from requests.status_codes import codes
from tarvis.common import secrets
import tarvis.common.environ
from tarvis.common.environ import DeploymentType
from tarvis.common.trading import Exchange, Order, OrderSide, OrderType, TradingPolicy
from threading import Lock
import time as native_time


class ResponseDecimal(Response):
    def json(self, **kwargs):
        return super().json(parse_float=Decimal, **kwargs)


class SessionDecimal(Session):
    def send(self, request, **kwargs):
        r = super().send(request, **kwargs)
        r.__class__ = ResponseDecimal
        return r


class BinanceVersion(Enum):
    SPOT = 0
    MARGIN = 1
    USD_M_PERPETUAL = 2


class BinanceExchange(Exchange):
    EXCHANGE_NAME = "Binance"

    _ORDER_TYPE_TO_BINANCE_SPOT_MARGIN = {
        OrderType.MARKET: "MARKET",
        OrderType.LIMIT: "LIMIT",
        OrderType.STOP_LOSS: "STOP_LOSS_LIMIT",
    }
    _ORDER_TYPE_TO_TARVIS_SPOT_MARGIN = dict(
        (value, key) for key, value in _ORDER_TYPE_TO_BINANCE_SPOT_MARGIN.items()
    )

    _ORDER_TYPE_TO_BINANCE_FUTURES = {
        OrderType.MARKET: "MARKET",
        OrderType.LIMIT: "LIMIT",
        OrderType.STOP_LOSS: "STOP_MARKET",
    }
    _ORDER_TYPE_TO_TARVIS_FUTURES = dict(
        (value, key) for key, value in _ORDER_TYPE_TO_BINANCE_FUTURES.items()
    )

    _lock = Lock()
    _symbol_to_assets = {}
    _assets_to_symbol = {}

    def __init__(
        self,
        credentials_secret: str,
        version: str | BinanceVersion = BinanceVersion.SPOT,
    ):
        super().__init__()
        self.stop_loss_orders_supported = True

        credentials = secrets.get_secret(credentials_secret, decode_json=True)
        api_key = credentials["api_key"]
        api_secret = credentials["api_secret"]

        self._order_type_to_binance = self._ORDER_TYPE_TO_BINANCE_SPOT_MARGIN
        self._order_type_to_tarvis = self._ORDER_TYPE_TO_TARVIS_SPOT_MARGIN

        if isinstance(version, str):
            version = BinanceVersion[version.upper()]

        if version == BinanceVersion.MARGIN:
            raise NotImplementedError(
                "Margin is not supported until Binance "
                "adds support for it in the Testnet."
            )

        self._version = version
        match version:
            case BinanceVersion.SPOT | BinanceVersion.MARGIN:
                self.short_selling_supported = version == BinanceVersion.MARGIN
                self._perpetual = False
                self._quote_asset = None
                if tarvis.common.environ.deployment == DeploymentType.PRODUCTION:
                    base_url = "https://api.binance.com"
                else:
                    base_url = "https://testnet.binance.vision"
                self._client = Spot(
                    base_url=base_url,
                    api_key=api_key,
                    api_secret=api_secret,
                )
            case BinanceVersion.USD_M_PERPETUAL:
                self.short_selling_supported = True
                self._perpetual = True
                self._quote_asset = "USDT"
                self._order_type_to_binance = self._ORDER_TYPE_TO_BINANCE_FUTURES
                self._order_type_to_tarvis = self._ORDER_TYPE_TO_TARVIS_FUTURES
                if tarvis.common.environ.deployment == DeploymentType.PRODUCTION:
                    base_url = "https://fapi.binance.com"
                else:
                    base_url = "https://testnet.binancefuture.com"
                self._client = UMFutures(
                    base_url=base_url,
                    key=api_key,
                    secret=api_secret,
                )
            case _:
                raise ValueError("version not supported.")

        # Monkeypatch library to parse decimals correctly
        self._client.session.__class__ = SessionDecimal

    @staticmethod
    def _retry_rate_limited_call(_call_method, *args, **kwargs):
        try:
            response = _call_method(*args, **kwargs)
        except ClientError as client_exception:
            if client_exception.status_code == codes.too_many_requests:
                delay = client_exception.header.get("Retry-After", 0)
                native_time.sleep(float(delay))
                response = _call_method(*args, **kwargs)
            else:
                raise
        return response

    def _populate_symbol_assets_mappings(self):
        symbol_to_assets = self.__class__._symbol_to_assets.get(self._version)
        if symbol_to_assets is None:
            with self.__class__._lock:
                symbol_to_assets = self.__class__._symbol_to_assets.get(self._version)
                if symbol_to_assets is None:
                    symbol_to_assets = {}
                    assets_to_symbol = {}

                    response = self._retry_rate_limited_call(
                        self._client.exchange_info  # noqa
                    )

                    instruments = response["symbols"]
                    for instrument in instruments:
                        contract_type = instrument.get("contractType")
                        quote_asset = instrument["quoteAsset"]

                        if self._perpetual:
                            include_instrument = (
                                contract_type[:9] == "PERPETUAL"
                            ) and (quote_asset == self._quote_asset)
                        else:
                            include_instrument = contract_type is None

                        if include_instrument:
                            symbol = instrument["symbol"]
                            base_asset = instrument["baseAsset"]
                            asset_pair = (base_asset, quote_asset)
                            symbol_to_assets[symbol] = asset_pair
                            assets_to_symbol[asset_pair] = symbol

                    # Spot and margin share the same instruments
                    if not self._perpetual:
                        versions = [BinanceVersion.SPOT, BinanceVersion.MARGIN]
                    else:
                        versions = [self._version]

                    for version in versions:
                        self.__class__._symbol_to_assets[version] = symbol_to_assets
                        self.__class__._assets_to_symbol[version] = assets_to_symbol

    def _convert_symbol_to_assets(self, symbol: str):
        self._populate_symbol_assets_mappings()
        symbol_to_assets = self.__class__._symbol_to_assets[self._version]
        return symbol_to_assets.get(symbol)

    def _convert_assets_to_symbol(self, base_asset: str, quote_asset: str):
        self._populate_symbol_assets_mappings()
        assets_to_symbol = self.__class__._assets_to_symbol[self._version]
        symbol = assets_to_symbol.get((base_asset, quote_asset))
        if symbol is None:
            raise Exception(
                f'Missing pair "{base_asset}/{quote_asset}" in exchange information'
            )
        return symbol

    @staticmethod
    def _get_filter(filters: list, filter_type: str):
        for f in filters:
            if f["filterType"] == filter_type:
                return f
        return None

    def _create_policy(self, filters: list) -> TradingPolicy:
        notional_filter = self._get_filter(filters, "NOTIONAL")
        if notional_filter is None:
            notional_filter = self._get_filter(filters, "MIN_NOTIONAL")

        lot_size_filter = self._get_filter(filters, "LOT_SIZE")
        price_filter = self._get_filter(filters, "PRICE_FILTER")

        if notional_filter is None:
            minimum_order_value = 0
            maximum_order_value = None
        else:
            minimum_order_value = notional_filter.get("minNotional")
            if minimum_order_value is None:
                minimum_order_value = notional_filter.get("notional", 0)
            maximum_order_value = notional_filter.get("maxNotional")

        minimum_order_value = Decimal(minimum_order_value)
        if maximum_order_value is not None:
            maximum_order_value = Decimal(maximum_order_value)
        minimum_order_quantity = Decimal(lot_size_filter["minQty"])
        maximum_order_quantity = Decimal(lot_size_filter["maxQty"])
        quantity_precision = Decimal(lot_size_filter["stepSize"])
        price_precision = Decimal(price_filter["tickSize"])

        return TradingPolicy(
            minimum_order_quantity=minimum_order_quantity,
            maximum_order_quantity=maximum_order_quantity,
            minimum_order_value=minimum_order_value,
            maximum_order_value=maximum_order_value,
            quantity_precision=quantity_precision,
            price_precision=price_precision,
        )

    def get_policy(self, base_asset: str, quote_asset: str) -> TradingPolicy:
        symbol = self._convert_assets_to_symbol(base_asset, quote_asset)

        if self._perpetual:
            response = self._retry_rate_limited_call(self._client.exchange_info)  # noqa
        else:
            response = self._retry_rate_limited_call(
                self._client.exchange_info, symbol=symbol  # noqa
            )

        instruments = response["symbols"]
        filters = None
        for instrument in instruments:
            if instrument["symbol"] == symbol:
                filters = instrument["filters"]
                break

        if filters is None:
            raise Exception(f'Missing symbol "{symbol}" in policy information')

        return self._create_policy(filters)

    def get_policies(
        self, asset_pairs: list[tuple[str, str]]
    ) -> dict[tuple[str, str], TradingPolicy]:
        symbols = None
        if not self._perpetual:
            symbols = []
            for asset_pair in asset_pairs:
                base_asset, quote_asset = asset_pair
                symbol = self._convert_assets_to_symbol(base_asset, quote_asset)
                symbols.append(symbol)
            symbols = "[" + ",".join(symbols) + "]"

        response = self._retry_rate_limited_call(
            self._client.exchange_info, symbols=symbols  # noqa
        )
        instruments = response["symbols"]

        instrument_data = {}
        for instrument in instruments:
            symbol = instrument["symbol"]
            instrument_data[symbol] = instrument

        policies = {}
        for asset_pair in asset_pairs:
            base_asset, quote_asset = asset_pair
            symbol = self._convert_assets_to_symbol(base_asset, quote_asset)
            filters = instrument_data[symbol]["filters"]
            policies[asset_pair] = self._create_policy(filters)

        return policies

    def get_quote(self, base_asset: str, quote_asset: str) -> Decimal:
        symbol = self._convert_assets_to_symbol(base_asset, quote_asset)
        response = self._retry_rate_limited_call(
            self._client.ticker_price, symbol=symbol  # noqa
        )
        price = response["price"]
        return Decimal(price)

    def get_positions(self) -> dict[str, Decimal]:
        results = {}
        response = self._retry_rate_limited_call(self._client.account)  # noqa

        match self._version:
            case BinanceVersion.SPOT:
                positions = response["balances"]
                for position in positions:
                    asset = position["asset"]
                    free = position["free"]
                    free = Decimal(free)
                    results[asset] = free

            # This is a starting point, not the full get_position implementation
            # for getting the positions in the margin version
            case BinanceVersion.MARGIN:
                positions = response["userAssets"]
                for position in positions:
                    asset = position["asset"]
                    free = position["free"]
                    free = Decimal(free)
                    results[asset] = free

            case _:
                quote_quantity = 0

                assets = response["assets"]
                for asset in assets:
                    if asset["asset"] == self._quote_asset:
                        balance = asset["marginBalance"]
                        balance = Decimal(balance)
                        quote_quantity = balance
                        break

                positions = response["positions"]
                for position in positions:
                    symbol = position["symbol"]
                    assets = self._convert_symbol_to_assets(symbol)
                    if assets is not None:
                        base_asset, quote_asset = assets
                        if quote_asset == self._quote_asset:
                            quantity = position["positionAmt"]
                            quantity = Decimal(quantity)
                            if quantity != 0:
                                price = position["entryPrice"]
                                price = Decimal(price)
                                results[base_asset] = quantity
                                quote_quantity -= quantity * price

                if quote_quantity != 0:
                    results[self._quote_asset] = quote_quantity

        return results

    def get_open_orders(self, base_asset: str, quote_asset: str) -> list[Order]:
        symbol = self._convert_assets_to_symbol(base_asset, quote_asset)

        match self._version:
            case BinanceVersion.SPOT:
                response = self._retry_rate_limited_call(
                    self._client.get_open_orders, symbol=symbol  # noqa
                )

            case BinanceVersion.MARGIN:
                response = self._retry_rate_limited_call(
                    self._client.margin_open_orders, symbol=symbol  # noqa
                )

            case _:
                response = self._retry_rate_limited_call(
                    self._client.get_orders, symbol=symbol  # noqa
                )

        results = []
        for binance_order in response:
            order_id = binance_order["orderId"]
            symbol = binance_order["symbol"]
            quantity = binance_order["origQty"]
            side = binance_order["side"]
            order_type = binance_order["type"]
            if order_type in ["STOP_LOSS", "STOP_MARKET"]:
                price = binance_order["stopPrice"]
            else:
                price = binance_order["price"]
            creation_time = binance_order["time"]
            filled_quantity = binance_order["executedQty"]

            assets = self._convert_symbol_to_assets(symbol)
            if assets is None:
                raise Exception(f'Missing symbol "{symbol}" in exchange information')

            base_asset, quote_asset = assets
            quantity = Decimal(quantity)
            price = Decimal(price)
            side = OrderSide[side]
            # noinspection PyBroadException
            try:
                order_type = self._order_type_to_tarvis[order_type]
            except:
                order_type = OrderType.UNSUPPORTED
            creation_time = float(creation_time) / 1000
            filled_quantity = Decimal(filled_quantity)
            meta_data = {"orderId": order_id}

            order = Order(
                base_asset,
                quote_asset,
                side,
                order_type,
                creation_time,
                quantity=quantity,
                price=price,
                filled_quantity=filled_quantity,
                meta_data=meta_data,
            )

            results.append(order)

        return results

    def place_order(
        self,
        policy: TradingPolicy,
        base_asset: str,
        quote_asset: str,
        side: OrderSide,
        order_type: OrderType,
        quantity: Decimal,
        price: Decimal = None,
        stop_loss_price: Decimal = None,
        increasing_position: bool = None,
    ):
        symbol = self._convert_assets_to_symbol(base_asset, quote_asset)
        binance_order_type = self._order_type_to_binance[order_type]
        quantity = str(quantity)
        binance_price = None
        binance_stop_price = None
        time_in_force = None

        if order_type == OrderType.LIMIT:
            binance_price = str(price)
            time_in_force = "GTC"
        elif order_type == OrderType.STOP_LOSS:
            binance_stop_price = str(stop_loss_price)
            time_in_force = "GTC"

            # Special case for stop loss orders on spot and margin, which are actually
            # stop limit orders, not stop market orders
            if not self._perpetual:
                if price is None:
                    price = stop_loss_price
                binance_price = str(price)

        match self._version:
            case BinanceVersion.SPOT:
                self._retry_rate_limited_call(
                    self._client.new_order,  # noqa
                    symbol=symbol,
                    side=side.name,
                    type=binance_order_type,
                    quantity=quantity,
                    price=binance_price,
                    stopPrice=binance_stop_price,
                    timeInForce=time_in_force,
                )

            case BinanceVersion.MARGIN:
                if increasing_position:
                    side_effect_type = "MARGIN_BUY"
                else:
                    side_effect_type = "AUTO_REPAY"

                self._retry_rate_limited_call(
                    self._client.new_margin_order,  # noqa
                    symbol=symbol,
                    side=side.name,
                    type=binance_order_type,
                    quantity=quantity,
                    price=binance_price,
                    stopPrice=binance_stop_price,
                    timeInForce=time_in_force,
                    sideEffectType=side_effect_type,
                )

            case _:
                reduce_only = None
                if increasing_position is not None:
                    reduce_only = str(not increasing_position).lower()

                self._retry_rate_limited_call(
                    self._client.new_order,  # noqa
                    symbol=symbol,
                    side=side.name,
                    type=binance_order_type,
                    quantity=quantity,
                    price=binance_price,
                    stopPrice=binance_stop_price,
                    timeInForce=time_in_force,
                    reduceOnly=reduce_only,
                )

    def cancel_order(self, order: Order):
        symbol = self._convert_assets_to_symbol(order.base_asset, order.quote_asset)
        if self._version == BinanceVersion.MARGIN:
            self._retry_rate_limited_call(
                self._client.cancel_margin_order,  # noqa
                symbol=symbol,
                orderId=order.meta_data["orderId"],
            )
        else:
            self._retry_rate_limited_call(
                self._client.cancel_order,  # noqa
                symbol=symbol,
                orderId=order.meta_data["orderId"],
            )
