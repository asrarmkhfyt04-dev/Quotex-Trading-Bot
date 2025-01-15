# tests/test_end_to_end.py

import pytest
import time

from bot.trade_executor import TradeExecutor
from bot.strategy import TradingStrategy
from bot.risk_management import RiskManager

@pytest.fixture(scope="module")
def setup_all():
    """
    Module-scoped fixture to initialize the entire bot suite once,
    then yield these objects to any test functions in this module.

    1) Creates a TradeExecutor (which logs in, toggles Demo)
    2) Initializes a TradingStrategy
    3) Initializes a RiskManager with default stake/profit percentages
    """
    # 1) Create the executor, which triggers login + toggle to Demo
    executor = TradeExecutor()

    # 2) Create the strategy
    strategy = TradingStrategy()

    # 3) Create the RiskManager with desired stake & profit
    risk_manager = RiskManager(stake_pct=0.02, profit_pct=0.04)  # 2% stake, 4% TP

    yield (executor, strategy, risk_manager)

    # Teardown: close the Selenium session
    executor.close()

def test_end_to_end_trade(setup_all):
    """
    Comprehensive test:
    1) Ensure we have a non-negative (ideally non-zero) account_balance
    2) Fetch market data, confirm 'last_price'
    3) Generate buy/sell/hold from the strategy
    4) Risk check -> trade_amount
    5) Place a trade if BUY or SELL
    """
    executor, strategy, risk_manager = setup_all

    # 1) Get current account balance
    account_balance = executor.get_account_balance()
    assert account_balance >= 0.0, "Account balance should be a non-negative float."

    # 2) Fetch market data (e.g., 'last_price')
    market_data = executor.fetch_market_data()
    assert "last_price" in market_data, "Market data should contain 'last_price'."

    # 3) Generate strategy signal
    signal = strategy.generate_signal(market_data)
    assert signal in ["BUY", "SELL", "HOLD"], f"Unexpected signal: {signal}"

    # 4) Compute position size
    trade_amount = risk_manager.check_position_size(account_balance)
    assert trade_amount > 0.0, "Trade amount should be greater than zero."

    # 5) Place trade if BUY or SELL
    if signal == "BUY":
        executor.set_investment_amount(trade_amount)
        executor.place_trade("UP")
        time.sleep(2)  # optional wait to confirm
    elif signal == "SELL":
        executor.set_investment_amount(trade_amount)
        executor.place_trade("DOWN")
        time.sleep(2)

    # If "HOLD," no trade is placed. 
    # Finally:
    assert True, "End-to-end test completed without errors."
