# risk_management.py - معدل للعمل على Android

class RiskManager:
    """
    إدارة المخاطر للروبوت
    """

    def __init__(self, stake_pct=0.02, profit_pct=0.04, max_daily_loss=0.10):
        """
        :param stake_pct: نسبة المبلغ المستثمر من الرصيد (مثال 0.02 = 2%)
        :param profit_pct: نسبة الربح المستهدف (مثال 0.04 = 4%)
        :param max_daily_loss: نسبة الخسارة اليومية القصوى (مثال 0.10 = 10%)
        """
        self.stake_pct = stake_pct
        self.profit_pct = profit_pct
        self.max_daily_loss = max_daily_loss
        self.daily_loss = 0
        self.daily_profit = 0
        self.initial_balance = 0
        self.trades_today = 0

    def initialize_daily(self, account_balance):
        """
        بدء يوم تداول جديد
        """
        self.initial_balance = account_balance
        self.daily_loss = 0
        self.daily_profit = 0
        self.trades_today = 0

    def check_position_size(self, account_balance):
        """
        حساب حجم الصفقة بناءً على الرصيد الحالي
        """
        return account_balance * self.stake_pct

    def can_trade(self, account_balance):
        """
        التحقق إذا كان يمكن فتح صفقة جديدة
        """
        # التحقق من حد الخسارة اليومي
        current_loss = self.initial_balance - account_balance
        if current_loss > (self.initial_balance * self.max_daily_loss):
            return False, f"تجاوز حد الخسارة اليومي {self.max_daily_loss * 100}%"
        
        # الحد الأقصى 20 صفقة في اليوم
        if self.trades_today >= 20:
            return False, "تم الوصول للحد الأقصى للصفقات اليومية (20 صفقة)"
        
        return True, "يمكن التداول"

    def update_result(self, result, amount):
        """
        تحديث نتائج التداول
        """
        self.trades_today += 1
        
        if result == "win":
            self.daily_profit += amount * 0.8
        else:
            self.daily_loss += amount

    def check_streak_limits(self, win_streak, loss_streak):
        """
        التحقق من حدود سلسلة الأرباح والخسائر
        """
        # وقف بعد 8 صفقات ربح متتالية
        if win_streak >= 8:
            return False, "تم تحقيق 8 صفقات ربح متتالية - إيقاف البوت"
        
        # وقف بعد صفقتين خسارة متتالية
        if loss_streak >= 2:
            return False, "تم تحقيق صفقتين خسارة متتالية - إيقاف البوت"
        
        return True, "ضمن الحدود"

    def get_optimal_amount(self, account_balance, signal_confidence):
        """
        حساب المبلغ الأمثل بناءً على الثقة في الإشارة
        """
        base_amount = account_balance * self.stake_pct
        
        # تعديل المبلغ حسب نسبة الثقة (70-100% فقط)
        if signal_confidence >= 85:
            multiplier = 1.0
        elif signal_confidence >= 75:
            multiplier = 0.75
        elif signal_confidence >= 70:
            multiplier = 0.5
        else:
            multiplier = 0  # لا تتداول إذا الثقة أقل من 70%
        
        return base_amount * multiplier

    def get_take_profit_balance(self, account_balance):
        """
        حساب حد الربح المستهدف
        """
        return account_balance * (1.0 + self.profit_pct)

    def get_stop_loss_balance(self, account_balance):
        """
        حساب حد وقف الخسارة
        """
        return account_balance * (1.0 - self.stake_pct)
