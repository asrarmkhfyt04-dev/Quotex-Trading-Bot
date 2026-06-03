# realtime_analyzer.py - تحليل فوري حقيقي للشمعات

import time
import math
import threading
from kivy.logger import Logger

class RealtimeAnalyzer:
    """
    تحليل فوري للشمعات وإشارات التداول
    """
    
    def __init__(self, strategy, risk_manager):
        self.strategy = strategy
        self.risk_manager = risk_manager
        self.last_signal = "HOLD"
        self.signal_confidence = 0
        self.last_analysis_time = 0
        self.analysis_interval = 30  # ثواني بين التحليلات
        
    def analyze_market(self, ohlcv_data):
        """
        تحليل السوق وإرجاع إشارة مع نسبة ثقة
        """
        if not ohlcv_data or len(ohlcv_data) < 20:
            return "HOLD", 0
        
        try:
            # استخدام الستراتيجية المخصصة
            signal = self.strategy.generate_signal(ohlcv_data)
            confidence = self.strategy.get_signal_confidence(ohlcv_data)
            
            self.last_signal = signal
            self.signal_confidence = confidence
            
            Logger.info(f"Analyzer: الإشارة = {signal}, الثقة = {confidence}%")
            
            return signal, confidence
            
        except Exception as e:
            Logger.error(f"Analyzer: خطأ في التحليل - {e}")
            return "HOLD", 0
    
    def should_trade(self, signal, confidence, current_balance):
        """
        تحديد ما إذا كان يجب التداول بناءً على الإشارة والثقة والرصيد
        """
        # شروط التداول
        if signal == "HOLD":
            return False, "لا توجد إشارة"
        
        if confidence < 70:
            return False, f"الثقة منخفضة ({confidence}% < 70%)"
        
        can_trade, reason = self.risk_manager.can_trade(current_balance)
        if not can_trade:
            return False, reason
        
        return True, "يمكن التداول"
    
    def calculate_entry_price(self, ohlcv_data, signal):
        """
        حساب سعر الدخول المناسب
        """
        if not ohlcv_data:
            return 0
        
        current_close = ohlcv_data[-1].get('close', 0)
        
        if signal == "BUY":
            # شراء عند سعر الطلب (قليل أعلى)
            return current_close * 1.0005
        else:
            # بيع عند سعر العرض (قليل أقل)
            return current_close * 0.9995
    
    def calculate_stop_loss(self, entry_price, signal, atr_value=0.002):
        """
        حساب وقف الخسارة
        """
        if signal == "BUY":
            return entry_price * (1 - atr_value)
        else:
            return entry_price * (1 + atr_value)
    
    def calculate_take_profit(self, entry_price, signal, risk_reward_ratio=2):
        """
        حساب جني الأرباح
        """
        stop_loss = self.calculate_stop_loss(entry_price, signal)
        
        if signal == "BUY":
            risk = entry_price - stop_loss
            return entry_price + (risk * risk_reward_ratio)
        else:
            risk = stop_loss - entry_price
            return entry_price - (risk * risk_reward_ratio)
    
    def detect_market_trend(self, ohlcv_data, period=20):
        """
        اكتشاف اتجاه السوق
        """
        if len(ohlcv_data) < period:
            return "NEUTRAL"
        
        # حساب المتوسطات المتحركة البسيطة
        closes = [c.get('close', 0) for c in ohlcv_data[-period:]]
        sma_fast = sum(closes[-10:]) / 10
        sma_slow = sum(closes) / period
        
        if sma_fast > sma_slow * 1.002:
            return "UPTREND"
        elif sma_fast < sma_slow * 0.998:
            return "DOWNTREND"
        else:
            return "SIDEWAYS"
    
    def get_market_volatility(self, ohlcv_data, period=14):
        """
        حساب التقلبات في السوق
        """
        if len(ohlcv_data) < period:
            return 0
        
        highs = [c.get('high', 0) for c in ohlcv_data[-period:]]
        lows = [c.get('low', 0) for c in ohlcv_data[-period:]]
        
        avg_range = sum([highs[i] - lows[i] for i in range(period)]) / period
        current_price = ohlcv_data[-1].get('close', 1)
        
        return (avg_range / current_price) * 100
    
    def get_support_resistance(self, ohlcv_data, period=50):
        """
        حساب مستويات الدعم والمقاومة
        """
        if len(ohlcv_data) < period:
            return 0, 0
        
        highs = [c.get('high', 0) for c in ohlcv_data[-period:]]
        lows = [c.get('low', 0) for c in ohlcv_data[-period:]]
        
        resistance = max(highs)
        support = min(lows)
        
        return support, resistance
    
    def is_good_entry(self, current_price, support, resistance, signal):
        """
        تحديد ما إذا كان السعر الحالي مناسباً للدخول
        """
        if signal == "BUY":
            # الشراء عند مستويات الدعم
            distance_to_support = (current_price - support) / current_price * 100
            return distance_to_support <= 0.5  # في حدود 0.5% من الدعم
        else:
            # البيع عند مستويات المقاومة
            distance_to_resistance = (resistance - current_price) / current_price * 100
            return distance_to_resistance <= 0.5  # في حدود 0.5% من المقاومة
