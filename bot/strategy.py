# strategy.py

import pandas as pd

# Import custom modules
from .indicators import calculate_rsi, calculate_macd, calculate_bollinger_bands

class TradingStrategy:
    def __init__(self, rsi_buy=25, rsi_sell=75):
        """
        A stricter strategy requiring triple confluence of 
        RSI, MACD, and Bollinger Bands to generate signals.

        :param rsi_buy: RSI threshold below which we consider oversold (default 25)
        :param rsi_sell: RSI threshold above which we consider overbought (default 75)
        """
        self.rsi_buy = rsi_buy
        self.rsi_sell = rsi_sell

    def generate_signal(self, market_data: pd.DataFrame) -> str:
        """
        Decide whether to 'BUY', 'SELL', or 'HOLD' based on:
          1) RSI crossing below/above stricter thresholds (25 / 75)
          2) MACD bullish/bearish crossover
          3) Price touching or crossing Bollinger Bands

        :param market_data: A DataFrame with a 'close' column at minimum 
                            (and enough rows for RSI/MACD/Boll. calculations)
        :return: 'BUY', 'SELL', or 'HOLD'
        """

        # Ensure we have enough rows to compute indicators. 
        # For a 14-bar RSI and ~26-bar MACD, let's require at least 26 bars:
        if len(market_data) < 26:
            return "HOLD"

        # 1) Calculate RSI
        rsi_series = calculate_rsi(market_data, period=14)
        current_rsi = rsi_series.iloc[-1]

        # 2) Calculate MACD
        macd_df = calculate_macd(market_data)
        # Example columns might be: ['MACD_12_26_9', 'MACDs_12_26_9', 'MACDh_12_26_9']
        macd_col = [c for c in macd_df.columns if c.startswith("MACD_") and not c.startswith("MACDh_")][0]
        signal_col = [c for c in macd_df.columns if c.startswith("MACDs_")][0]

        macd_line_current  = macd_df[macd_col].iloc[-1]
        macd_line_previous = macd_df[macd_col].iloc[-2]
        macd_signal_current  = macd_df[signal_col].iloc[-1]
        macd_signal_previous = macd_df[signal_col].iloc[-2]

        # 3) Bollinger Bands
        bb_df = calculate_bollinger_bands(market_data)
        # Example columns: ['BBL_20_2.0', 'BBM_20_2.0', 'BBU_20_2.0']
        bbl_col = [c for c in bb_df.columns if c.startswith("BBL")][0]  # Lower band
        bbu_col = [c for c in bb_df.columns if c.startswith("BBU")][0]  # Upper band

        price_current = market_data["close"].iloc[-1]
        lower_band    = bb_df[bbl_col].iloc[-1]
        upper_band    = bb_df[bbu_col].iloc[-1]

        # Check if price is near/below the lower band or near/above the upper band
        touching_lower_band = (price_current <= lower_band)
        touching_upper_band = (price_current >= upper_band)

        # RSI Logic
        rsi_buy_signal  = (current_rsi < self.rsi_buy)
        rsi_sell_signal = (current_rsi > self.rsi_sell)

        # MACD Crossover Logic
        macd_bullish_cross = (
            macd_line_current > macd_signal_current and
            macd_line_previous <= macd_signal_previous
        )
        macd_bearish_cross = (
            macd_line_current < macd_signal_current and
            macd_line_previous >= macd_signal_previous
        )

        # Final Confluence
        # BUY if RSI < 25, MACD bullish cross, and price <= lower Band
        if rsi_buy_signal and macd_bullish_cross and touching_lower_band:
            return "BUY"

        # SELL if RSI > 75, MACD bearish cross, and price >= upper Band
        elif rsi_sell_signal and macd_bearish_cross and touching_upper_band:
            return "SELL"

        else:
            return "HOLD"
