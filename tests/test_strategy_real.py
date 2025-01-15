# tests/test_strategy_real.py

import pytest
import pandas as pd
from bot.strategy import TradingStrategy

@pytest.fixture
def strategy():
    return TradingStrategy()

def test_buy_with_real_data(strategy):
    """
    Two-phase price pattern (100 bars):
      - 70 bars descending by 0.04 from ~2.0 => ~ -0.8
      - 30 bars ascending by 0.06 => ~1.0
    Attempt to produce RSI <30 & bullish MACD cross => 'BUY'.
    """
    prices = []
    for i in range(70):
        prices.append(2.0 - i * 0.04)
    for i in range(30):
        prices.append(prices[-1] + 0.06)

    mock_data = pd.DataFrame({"close": prices})
    signal = strategy.generate_signal(mock_data)
    assert signal == "BUY", f"Expected 'BUY' but got {signal}"

def test_sell_with_real_data(strategy):
    """
    Two-phase price pattern (100 bars):
      - 70 bars ascending by 0.04 => ~3.8
      - 30 bars descending by 0.06 => ~2.0
    Attempt to produce RSI >70 & bearish MACD cross => 'SELL'.
    """
    prices = []
    for i in range(70):
        prices.append(1.0 + i * 0.04)
    for i in range(30):
        prices.append(prices[-1] - 0.06)

    mock_data = pd.DataFrame({"close": prices})
    signal = strategy.generate_signal(mock_data)
    assert signal == "SELL", f"Expected 'SELL' but got {signal}"

def test_hold_with_real_data(strategy):
    """
    ~80 bars lightly oscillating => 'HOLD'.
    """
    prices = []
    base_price = 1.20
    for i in range(80):
        if i % 2 == 0:
            base_price += 0.01
        else:
            base_price -= 0.01
        prices.append(base_price)

    mock_data = pd.DataFrame({"close": prices})
    signal = strategy.generate_signal(mock_data)
    assert signal == "HOLD", f"Expected 'HOLD' but got {signal}"
