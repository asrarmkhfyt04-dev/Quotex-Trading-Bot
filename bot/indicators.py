# indicators.py - معدل للعمل على Android (بدون pandas و pandas_ta)

import math

def calculate_rsi(data, period=14):
    """
    حساب RSI بدون pandas
    data: قائمة من القاموسات تحتوي على 'close'
    period: فترة الحساب
    """
    if len(data) < period + 1:
        return 50
    
    gains = 0
    losses = 0
    
    for i in range(len(data) - period, len(data)):
        current_close = data[i].get('close', 0)
        previous_close = data[i-1].get('close', 0)
        change = current_close - previous_close
        
        if change > 0:
            gains += change
        else:
            losses += abs(change)
    
    if losses == 0:
        return 100
    
    rs = gains / losses
    rsi = 100 - (100 / (1 + rs))
    
    return rsi

def calculate_macd(data, fast=12, slow=26, signal=9):
    """
    حساب MACD بدون pandas
    """
    if len(data) < slow + signal:
        return {
            'macd_line': 0,
            'signal_line': 0,
            'histogram': 0
        }
    
    # حساب EMA السريعة والبطيئة
    ema_fast = calculate_ema(data, fast)
    ema_slow = calculate_ema(data, slow)
    
    # خط MACD
    macd_line = ema_fast - ema_slow
    
    # حساب خط الإشارة (EMA لخط MACD)
    macd_values = []
    for i in range(len(data)):
        if i < slow:
            macd_values.append(0)
        else:
            ema_fast_i = calculate_ema_at_index(data, i, fast)
            ema_slow_i = calculate_ema_at_index(data, i, slow)
            macd_values.append(ema_fast_i - ema_slow_i)
    
    signal_line = calculate_ema_from_list(macd_values, signal)
    
    return {
        'macd_line': macd_line,
        'signal_line': signal_line,
        'histogram': macd_line - signal_line
    }

def calculate_bollinger_bands(data, period=20, std_dev=2.0):
    """
    حساب بولينجر باند بدون pandas
    """
    if len(data) < period:
        return {
            'upper': 0,
            'middle': 0,
            'lower': 0
        }
    
    # حساب المتوسط المتحرك
    recent_closes = [d.get('close', 0) for d in data[-period:]]
    middle_band = sum(recent_closes) / period
    
    # حساب الانحراف المعياري
    variance = sum([(x - middle_band) ** 2 for x in recent_closes]) / period
    std = math.sqrt(variance)
    
    return {
        'upper': middle_band + (std_dev * std),
        'middle': middle_band,
        'lower': middle_band - (std_dev * std)
    }

def calculate_ema(data, period):
    """
    حساب EMA (Exponential Moving Average)
    """
    if len(data) < period:
        return data[-1].get('close', 0) if data else 0
    
    multiplier = 2 / (period + 1)
    closes = [d.get('close', 0) for d in data]
    
    ema = sum(closes[:period]) / period
    
    for price in closes[period:]:
        ema = (price - ema) * multiplier + ema
    
    return ema

def calculate_ema_at_index(data, index, period):
    """
    حساب EMA عند مؤشر محدد
    """
    if index < period:
        return data[index].get('close', 0)
    
    multiplier = 2 / (period + 1)
    closes = [d.get('close', 0) for d in data[:index+1]]
    
    ema = sum(closes[:period]) / period
    
    for i in range(period, index + 1):
        ema = (closes[i] - ema) * multiplier + ema
    
    return ema

def calculate_ema_from_list(values, period):
    """
    حساب EMA من قائمة قيم
    """
    if len(values) < period:
        return values[-1] if values else 0
    
    multiplier = 2 / (period + 1)
    ema = sum(values[:period]) / period
    
    for val in values[period:]:
        ema = (val - ema) * multiplier + ema
    
    return ema

def calculate_sma(data, period):
    """
    حساب SMA (Simple Moving Average)
    """
    if len(data) < period:
        return data[-1].get('close', 0) if data else 0
    
    closes = [d.get('close', 0) for d in data[-period:]]
    return sum(closes) / period
