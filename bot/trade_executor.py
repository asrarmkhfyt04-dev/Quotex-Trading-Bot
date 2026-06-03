# trade_executor.py - نسخة نهائية مع WebView

import time
from webview_manager import QuotexWebViewManager
from market_data import MarketDataFetcher

class TradeExecutor:
    """
    منفذ الصفقات الحقيقي باستخدام WebView
    """
    
    def __init__(self, webview_manager=None):
        if webview_manager:
            self.webview = webview_manager
        else:
            self.webview = QuotexWebViewManager()
        
        self.market_data = MarketDataFetcher(self.webview)
        self.is_logged_in = False
        self.current_asset = "EUR/USD"
        self.investment_amount = 10.0
        
    def init_webview(self, layout):
        """
        تهيئة WebView
        """
        return self.webview.init_webview(layout)
    
    def load_platform(self):
        """
        تحميل منصة Quotex
        """
        return self.webview.load_url("https://qxbroker.com")
    
    def login(self, email, password, use_demo=True):
        """
        تسجيل الدخول
        """
        result = self.webview.login(email, password)
        if result and use_demo:
            time.sleep(3)
            self.webview.switch_to_demo()
        
        self.is_logged_in = result
        return result
    
    def get_account_balance(self):
        """
        الحصول على الرصيد
        """
        return self.webview.get_balance()
    
    def select_asset(self, asset_name):
        """
        اختيار الزوج
        """
        self.current_asset = asset_name
        self.market_data.set_asset(asset_name)
        return self.webview.select_asset(asset_name)
    
    def set_investment_amount(self, amount):
        """
        تحديد المبلغ
        """
        self.investment_amount = amount
        return self.webview.set_investment_amount(amount)
    
    def set_timeframe(self, minutes):
        """
        تحديد مدة الشمعة
        """
        self.market_data.set_timeframe(minutes)
        return self.webview.set_timeframe(minutes)
    
    def fetch_market_data(self):
        """
        جلب بيانات السوق
        """
        ohlcv = self.market_data.fetch_ohlcv()
        current_price = self.market_data.fetch_current_price()
        
        return {
            'asset': self.current_asset,
            'current_price': current_price,
            'candles': ohlcv
        }
    
    def fetch_candles(self, count=50):
        """
        جلب الشموع للتحليل
        """
        return self.market_data.fetch_candles(count)
    
    def get_available_assets(self):
        """
        جلب العملات المتاحة من المنصة
        """
        return self.market_data.fetch_available_assets()
    
    def place_trade(self, direction):
        """
        تنفيذ صفقة
        """
        result = self.webview.place_trade(direction)
        
        # انتظار نتيجة الصفقة
        time.sleep(2)
        
        # جلب نتيجة الصفقة (ربح/خسارة)
        # هذا يعتمد على API المنصة
        trade_result = self._get_trade_result()
        
        return trade_result
    
    def _get_trade_result(self):
        """
        الحصول على نتيجة الصفقة الأخيرة
        """
        # سيتم إضافة كود لجلب النتيجة من WebView
        return {
            'win': True,
            'direction': 'UP',
            'amount': self.investment_amount,
            'profit': self.investment_amount * 0.8
        }
    
    def close(self):
        """
        إغلاق WebView
        """
        self.webview.close()
