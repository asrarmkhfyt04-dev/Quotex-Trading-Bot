# indicators.py

import pandas as pd
import pandas_ta as ta

from .config import (
    RSI_THRESHOLD,
    MACD_FAST,
    MACD_SLOW,
    MACD_SIGNAL,
    BOLLINGER_PERIOD,
    BOLLINGER_STD_DEV
)

def calculate_rsi(
    data: pd.DataFrame,
    period: int = 14
) -> pd.Series:
    """
    Calculate RSI (Relative Strength Index) using pandas_ta.

    :param data: A DataFrame with at least a 'close' column.
    :param period: Lookback period for RSI (default=14).
    :return: A Series of RSI values, same length as 'data'.
    :raises ValueError: If 'close' column is missing.
    """
    if "close" not in data.columns:
        raise ValueError("Data must contain a 'close' column for RSI calculation.")

    return ta.rsi(data["close"], length=period)

def calculate_macd(
    data: pd.DataFrame,
    fast: int = MACD_FAST,
    slow: int = MACD_SLOW,
    signal: int = MACD_SIGNAL
) -> pd.DataFrame:
    """
    Calculate MACD using pandas_ta.

    :param data: A DataFrame with at least a 'close' column.
    :param fast: Fast period (default=MACD_FAST from config).
    :param slow: Slow period (default=MACD_SLOW).
    :param signal: Signal period (default=MACD_SIGNAL).
    :return: A DataFrame with columns like:
             [ 'MACD_12_26_9', 'MACDs_12_26_9', 'MACDh_12_26_9' ].
    :raises ValueError: If 'close' column is missing.
    """
    if "close" not in data.columns:
        raise ValueError("Data must contain a 'close' column for MACD calculation.")

    macd_df = ta.macd(data["close"], fast=fast, slow=slow, signal=signal)
    return macd_df

def calculate_bollinger_bands(
    data: pd.DataFrame,
    period: int = BOLLINGER_PERIOD,
    std_dev: float = BOLLINGER_STD_DEV
) -> pd.DataFrame:
    """
    Calculate Bollinger Bands using pandas_ta.

    :param data: A DataFrame with at least a 'close' column.
    :param period: Length for the moving average (default=BOLLINGER_PERIOD).
    :param std_dev: # of standard deviations above/below the MA (default=BOLLINGER_STD_DEV).
    :return: A DataFrame with columns like:
             [ 'BBL_20_2.0', 'BBM_20_2.0', 'BBU_20_2.0', 'BBB_20_2.0', 'BBP_20_2.0' ]
    :raises ValueError: If 'close' column is missing.
    """
    if "close" not in data.columns:
        raise ValueError("Data must contain a 'close' column for Bollinger Bands calculation.")

    bb_df = ta.bbands(data["close"], length=period, std=std_dev)
    return bb_df
