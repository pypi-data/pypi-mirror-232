from decimal import Decimal
import logging
from tarvis.common.trading import Exchange


class ExchangeAccountDivision:
    def __init__(
        self,
        exchange_base_asset: str,
        indicator_quote_asset: str,
        allocation: Decimal = 1,
        indicator_base_asset: str = None,
        indicator_price_conversion: Decimal = 1,
    ):
        if allocation <= 0:
            raise ValueError("allocation must be greater than 0.")
        if indicator_base_asset is None:
            indicator_base_asset = exchange_base_asset
        if indicator_price_conversion <= 0:
            raise ValueError("indicator_price_conversion must be greater than 0.")

        self.exchange_base_asset = exchange_base_asset
        self.allocation = Decimal(allocation)
        self.indicator_base_asset = indicator_base_asset
        self.indicator_quote_asset = indicator_quote_asset
        self.indicator_asset_pair = (indicator_base_asset, indicator_quote_asset)
        self.indicator_price_conversion = Decimal(indicator_price_conversion)

    def __json__(self):
        return self.__dict__


class ExchangeAccount:
    def __init__(
        self,
        exchange_account_id: int,
        exchange: Exchange,
        divisions: list[ExchangeAccountDivision],
        exchange_quote_asset: str,
        reserve_minimum: Decimal,
        reserve_fraction: Decimal = 0,
        position_limit: Decimal = None,
        leverage_multiplier: Decimal = 1,
        leverage_limit: Decimal = 1,
        allocation_deviation_limit: Decimal = Decimal("0.01"),
        policy_cache_expiration: float = 3600,
    ):
        if not divisions:
            raise ValueError("divisions is empty.")
        allocation_total = 0
        indicator_asset_pairs = []
        exchange_asset_pairs = []
        for division in divisions:
            allocation_total += division.allocation
            indicator_asset_pairs.append(division.indicator_asset_pair)
            exchange_asset_pairs.append(
                (division.exchange_base_asset, exchange_quote_asset)
            )
        if allocation_total > 1:
            logging.warning(
                "Total allocations is greater than 100%",
                extra={
                    "exchange_account_id": exchange_account_id,
                    "exchange": exchange.EXCHANGE_NAME,
                    "allocation_total": allocation_total,
                },
            )
        reserve_minimum = Decimal(reserve_minimum)
        if reserve_minimum < 0:
            raise ValueError("reserve_minimum must be greater than or equal to 0.")
        if (reserve_fraction < 0) or (reserve_fraction >= 1):
            raise ValueError(
                "reserve_fraction must be equal to 0 or greater than 0 and less than 1."
            )
        if position_limit is not None:
            position_limit = Decimal(position_limit)
            if position_limit <= 0:
                raise ValueError("position_limit must be greater than 0.")
        leverage_multiplier = Decimal(leverage_multiplier)
        if leverage_multiplier <= 0:
            raise ValueError("leverage_multiplier must be greater than 0.")
        leverage_limit = Decimal(leverage_limit)
        if leverage_limit <= 0:
            raise ValueError("leverage_limit must be greater than 0.")
        allocation_deviation_limit = Decimal(allocation_deviation_limit)
        if (allocation_deviation_limit < 0) or (allocation_deviation_limit >= 1):
            raise ValueError(
                "allocation_deviation_limit must be equal to 0 "
                "or greater than 0 and less than 1."
            )

        self.exchange_account_id = exchange_account_id
        self.exchange = exchange
        self.divisions = divisions
        self.exchange_quote_asset = exchange_quote_asset
        self.indicator_asset_pairs = set(indicator_asset_pairs)
        self.exchange_asset_pairs = list(set(exchange_asset_pairs))
        self.reserve_minimum = Decimal(reserve_minimum)
        self.reserve_fraction = Decimal(reserve_fraction)
        self.position_limit = position_limit
        self.leverage_multiplier = leverage_multiplier
        self.leverage_limit = leverage_limit
        self.allocation_deviation_limit = allocation_deviation_limit
        self.policy_cache_expiration = float(policy_cache_expiration)

    def indicator_asset_pairs_mapped(self, mapped_pairs: list[tuple[str, str]]) -> bool:
        return any((True for x in mapped_pairs if x in self.indicator_asset_pairs))

    def __json__(self):
        results = self.__dict__.copy()
        results["exchange"] = self.exchange.EXCHANGE_NAME
        return results
