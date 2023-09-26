import common  # noqa
from decimal import Decimal
import logging
from tarvis.atb import AdvancedTradingBot, ExchangeAccount, ExchangeAccountDivision
from tarvis.common import time
from tarvis.common.trading import MarketPosition, TradingPolicy
from tarvis.exchange.test import TestExchange
from tarvis.indicators.test import TestIndicatorSource
import pytest  # noqa

MINIMUM_ORDER_AMOUNT = Decimal(1)
MAXIMUM_ORDER_AMOUNT = Decimal(100)
QUANTITY_DECIMALS = 3
PRICE_DECIMALS = 2


def _create_policy():
    return TradingPolicy(
        minimum_order_quantity=MINIMUM_ORDER_AMOUNT,
        maximum_order_quantity=MAXIMUM_ORDER_AMOUNT,
        quantity_decimals=QUANTITY_DECIMALS,
        price_decimals=PRICE_DECIMALS,
    )


def test_all():
    _BASE_ASSET = "BTC"
    _BASE_ASSET_START_AMOUNT = Decimal("0")
    _QUOTE_ASSET = "USD"
    _QUOTE_ASSET_START_AMOUNT = Decimal("100000")
    _PRICE_INITIAL = Decimal("1000")
    _PRICE_VARIANCE = Decimal("100")
    _PRICE_LOW = _PRICE_INITIAL - _PRICE_VARIANCE
    _PRICE_HIGH = _PRICE_INITIAL + _PRICE_VARIANCE
    _NUM_TRANSITIONS = 20
    _NUM_UPDATE_ITERATIONS = 5
    _START_TIME = 100000
    _STEP_TIME = 5000
    _END_TIME = _START_TIME + ((_NUM_TRANSITIONS + 1) * _STEP_TIME)
    _TRADE_OFFSET = 100
    source = TestIndicatorSource()
    exchange = TestExchange()
    policy = _create_policy()
    exchange.set_policy(_BASE_ASSET, _QUOTE_ASSET, policy)
    trading_policies = {(_BASE_ASSET, _QUOTE_ASSET): policy}
    divisions = [ExchangeAccountDivision(_BASE_ASSET, _QUOTE_ASSET)]
    account = ExchangeAccount(
        exchange_account_id=0,
        exchange=exchange,
        divisions=divisions,
        exchange_quote_asset=_QUOTE_ASSET,
        reserve_minimum=Decimal("1000"),
        leverage_multiplier=Decimal("1"),
        leverage_limit=Decimal("1"),
    )
    bot = AdvancedTradingBot(
        bot_id=0,
        indicator_source=source,
        accounts=[account],
        short_selling=True,
        interval=60,
        delay=20,
        retries=0,
        retry_delay=0,
        indicator_expiration=300,
        price_deviation_limit=Decimal("0.00025"),
        premium_limit=Decimal("0.0002"),
        stop_loss=Decimal("0.2"),
        watchdog_timeout=60,
    )
    exchange.set_position(_BASE_ASSET, _BASE_ASSET_START_AMOUNT)
    exchange.set_position(_QUOTE_ASSET, _QUOTE_ASSET_START_AMOUNT)

    positions = exchange.get_positions()
    logging.info(f"Balance: {positions}")

    exchange.set_quote(_BASE_ASSET, _QUOTE_ASSET, _PRICE_INITIAL)
    for indicator_time in range(_START_TIME, _END_TIME, _STEP_TIME):
        # Ensure that the test ends on a flat so that the quote assets are at a maximum
        if indicator_time == _END_TIME - _STEP_TIME:
            direction = MarketPosition.FLAT
        else:
            direction = source.get_next_direction_transition()
        source.add_simple_indicator(
            _BASE_ASSET, _QUOTE_ASSET, indicator_time, direction
        )
    for simulation_time in range(_START_TIME, _END_TIME, _STEP_TIME):
        trade_time = simulation_time + _TRADE_OFFSET
        time.set_artificial_time(trade_time, 0, allow_reset=True)
        indicator = source.get_indicator(trade_time, _BASE_ASSET, _QUOTE_ASSET)
        match indicator.direction:
            case MarketPosition.FLAT:
                exchange.set_quote(_BASE_ASSET, _QUOTE_ASSET, _PRICE_INITIAL)
            case MarketPosition.LONG:
                exchange.set_quote(_BASE_ASSET, _QUOTE_ASSET, _PRICE_LOW)
            case MarketPosition.SHORT:
                exchange.set_quote(_BASE_ASSET, _QUOTE_ASSET, _PRICE_HIGH)
        quotes = exchange.get_quotes(account.exchange_asset_pairs)
        for update_iteration in range(_NUM_UPDATE_ITERATIONS):
            bot._update_account_iteration(
                account=account,
                indicators={(_BASE_ASSET, _QUOTE_ASSET): indicator},
                trading_policies=trading_policies,
                quotes=quotes,
                log_extra_update_account={},
            )
            exchange.fill_orders()
            positions = exchange.get_positions()
            logging.info(f"Balance: {positions}")
    assert positions[_QUOTE_ASSET] > _QUOTE_ASSET_START_AMOUNT
