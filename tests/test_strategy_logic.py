import pytest
import pandas as pd
from unittest.mock import patch

from bot.strategy import TradingStrategy

@pytest.fixture
def strategy():
    """
    Creates a TradingStrategy instance with default rsi_buy=25, rsi_sell=75
    consistent with your stricter thresholds.
    """
    return TradingStrategy(rsi_buy=25, rsi_sell=75)

@patch("bot.strategy.calculate_bollinger_bands")
@patch("bot.strategy.calculate_macd")
@patch("bot.strategy.calculate_rsi")
def test_buy_logic(mock_rsi, mock_macd, mock_boll, strategy):
    """
    Expects a final 'BUY' if:
      - RSI < 25
      - MACD bullish cross
      - Price <= lower band
      - total bars >= 26 
    """

    # 1) We need at least 26 rows because your strategy checks `if len(market_data) < 26: return "HOLD"`.
    #    The final bar => RSI=20 => <25 => triggers rsi_buy_signal
    #    We'll keep 25 earlier bars with safe values (like RSI around 40), and the 26th bar => 20.
    rsi_series = [40]*25 + [20]  
    mock_rsi.return_value = pd.Series(rsi_series)

    # 2) MACD bullish cross at final bar:
    #    final bar => line=0.02 > signal=0.01
    #    second-last bar => line=-0.01 <= signal=0.00 => bullish cross
    #    We'll produce 26 rows in total.
    macd_line =    [-0.01]*25 + [ 0.02]
    macd_signal =  [ 0.00]*25 + [ 0.01]
    macdh =        [ 0.0 ]*26                # no None/NaN
    mock_macd.return_value = pd.DataFrame({
        "MACD_12_26_9":  macd_line,
        "MACDs_12_26_9": macd_signal,
        "MACDh_12_26_9": macdh,
    })

    # 3) Bollinger => final lower band ~1.05, final price=1.00 => triggers touching_lower_band
    #    26 rows, first 25 can be mid-range (like lower=1.10), final =>1.05
    bbl_list = [1.10]*25 + [1.05]  # Lower band
    bbm_list = [1.15]*25 + [1.10]  # Mid band
    bbu_list = [1.20]*25 + [1.15]  # Upper band
    mock_boll.return_value = pd.DataFrame({
        "BBL_20_2.0": bbl_list,
        "BBM_20_2.0": bbm_list,
        "BBU_20_2.0": bbu_list,
    })

    # 4) Market data => 26 rows. final bar => close=1.00 => below 1.05 => triggers touching_lower_band
    #    earlier bars can be 1.15 or 1.2, etc. 
    prices = [1.15]*25 + [1.00]
    mock_data = pd.DataFrame({"close": prices})

    # 5) Call strategy
    signal = strategy.generate_signal(mock_data)
    assert signal == "BUY", f"Expected 'BUY' but got {signal}"

@patch("bot.strategy.calculate_bollinger_bands")
@patch("bot.strategy.calculate_macd")
@patch("bot.strategy.calculate_rsi")
def test_sell_logic(mock_rsi, mock_macd, mock_boll, strategy):
    """
    Expects a final 'SELL' if:
      - RSI > 75
      - MACD bearish cross
      - Price >= upper band
      - total bars >= 26
    """

    # 1) At least 26 bars => final RSI=80 => >75 => triggers rsi_sell_signal
    rsi_series = [50]*25 + [80]
    mock_rsi.return_value = pd.Series(rsi_series)

    # 2) MACD => final bar => line=-0.02 < signal=-0.01 => line < signal
    #    second-last bar => line=0.02 >= signal=0.01 => bearish cross
    macd_line =    [ 0.02]*25 + [-0.02]
    macd_signal =  [ 0.01]*25 + [-0.01]
    macdh =        [ 0.0 ]*26  
    mock_macd.return_value = pd.DataFrame({
        "MACD_12_26_9":  macd_line,
        "MACDs_12_26_9": macd_signal,
        "MACDh_12_26_9": macdh,
    })

    # 3) Bollinger => final bar => upper=1.30 => price=1.35 => triggers touching_upper_band
    #    26 rows total, final upper =>1.30
    bbl_list = [1.10]*25 + [1.15] 
    bbm_list = [1.20]*25 + [1.25]
    bbu_list = [1.25]*25 + [1.30] 
    mock_boll.return_value = pd.DataFrame({
        "BBL_20_2.0": bbl_list,
        "BBM_20_2.0": bbm_list,
        "BBU_20_2.0": bbu_list,
    })

    # final price=1.35 => above 1.30
    prices = [1.20]*25 + [1.35]
    mock_data = pd.DataFrame({"close": prices})

    signal = strategy.generate_signal(mock_data)
    assert signal == "SELL", f"Expected 'SELL' but got {signal}"

@patch("bot.strategy.calculate_bollinger_bands")
@patch("bot.strategy.calculate_macd")
@patch("bot.strategy.calculate_rsi")
def test_hold_logic(mock_rsi, mock_macd, mock_boll, strategy):
    """
    If final bar doesn't satisfy buy or sell conditions => 'HOLD'.
    Also, if total bars <26 => returns 'HOLD'.
    We'll do a short test data with fewer than 26 bars or neutral values.
    """

    # For an unambiguous HOLD, let's just supply <26 bars => immediate 'HOLD'
    # e.g., 10 bars total
    mock_data = pd.DataFrame({"close": [1.15]*10})

    # Even if RSI is <25, the code won't see it because it short-circuits if len<26
    mock_rsi.return_value = pd.Series([None]*9 + [20.0])
    mock_macd.return_value = pd.DataFrame({
        "MACD_12_26_9":  [None]*10,
        "MACDs_12_26_9": [None]*10,
        "MACDh_12_26_9": [None]*10,
    })
    mock_boll.return_value = pd.DataFrame({
        "BBL_20_2.0": [None]*10,
        "BBM_20_2.0": [None]*10,
        "BBU_20_2.0": [None]*10,
    })

    signal = strategy.generate_signal(mock_data)
    assert signal == "HOLD", f"Expected 'HOLD' but got {signal}"
