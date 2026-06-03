# strategy.py - معدل للعمل على Android (بدون pandas)

import random
import math

class TradingStrategy:
    def __init__(self, rsi_buy=25, rsi_sell=75):
        """
        استراتيجية التداول المبسطة للأندرويد
        تعتمد على تحليل بسيط للشمعة الأخيرة
        """
        self.rsi_buy = rsi_buy
        self.rsi_sell = rsi_sell
        self.last_signals = []  # لتخزين آخر الإشارات
        
    def generate_signal(self, market_data):
        """
        تحليل السوق وإرجاع إشارة BUY أو SELL أو HOLD
        market_data: قاموس يحتوي على بيانات الشموع
        """
        
        # إذا كانت البيانات غير كافية
        if not market_data or len(market_data) < 10:
            return "HOLD"
        
        # حساب RSI مبسط
        current_rsi = self.calculate_simple_rsi(market_data)
        
        # حساب تقاطع مبسط
        price_trend = self.calculate_trend(market_data)
        
        # حساب مستويات الدعم والمقاومة
        support, resistance = self.calculate_support_resistance(market_data)
        current_price = market_data[-1].get('close', 0)
        
        # شروط الشراء
        if current_rsi < self.rsi_buy and price_trend == "UP":
            if current_price <= support * 1.002:  # قرب مستوى الدعم
                return "BUY"
        
        # شروط البيع
        if current_rsi > self.rsi_sell and price_trend == "DOWN":
            if current_price >= resistance * 0.998:  # قرب مستوى المقاومة
                return "SELL"
        
        return "HOLD"
    
    def calculate_simple_rsi(self, data):
        """
        حساب RSI مبسط بدون pandas
        """
        if len(data) < 15:
            return 50
        
        gains = 0
        losses = 0
        
        for i in range(len(data) - 14, len(data)):
            change = data[i].get('close', 0) - data[i-1].get('close', 0)
            if change > 0:
                gains += change
            else:
                losses += abs(change)
        
        if losses == 0:
            return 100
        
        rs = gains / losses
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def calculate_trend(self, data):
        """
        حساب اتجاه السعر (UP/DOWN/SIDEWAYS)
        """
        if len(data) < 5:
            return "SIDEWAYS"
        
        # مقارنة سعر الإغلاق الحالي مع متوسط آخر 5 شموع
        recent_closes = [c.get('close', 0) for c in data[-5:]]
        avg_close = sum(recent_closes) / len(recent_closes)
        current_close = data[-1].get('close', 0)
        
        if current_close > avg_close * 1.002:
            return "UP"
        elif current_close < avg_close * 0.998:
            return "DOWN"
        else:
            return "SIDEWAYS"
    
    def calculate_support_resistance(self, data):
        """
        حساب مستويات الدعم والمقاومة
        """
        if len(data) < 10:
            # قيم افتراضية
            current_price = data[-1].get('close', 100)
            return current_price * 0.99, current_price * 1.01
        
        highs = [c.get('high', 0) for c in data[-10:]]
        lows = [c.get('low', 0) for c in data[-10:]]
        
        resistance = max(highs)
        support = min(lows)
        
        return support, resistance
    
    def get_signal_confidence(self, market_data):
        """
        حساب نسبة الثقة في الإشارة (0-100)
        """
        signal = self.generate_signal(market_data)
        
        if signal == "HOLD":
            return 0
        
        current_rsi = self.calculate_simple_rsi(market_data)
        trend = self.calculate_trend(market_data)
        
        confidence = 50  # أساس
        
        # تعديل نسبة الثقة بناءً على RSI
        if signal == "BUY":
            confidence += (self.rsi_buy - current_rsi) * 2
        else:
            confidence += (current_rsi - self.rsi_sell) * 2
        
        # تعديل نسبة الثقة بناءً على الاتجاه
        if (signal == "BUY" and trend == "UP") or (signal == "SELL" and trend == "DOWN"):
            confidence += 15
        
        # تحديد النسبة بين 0 و 100
        return max(0, min(100, confidence))
