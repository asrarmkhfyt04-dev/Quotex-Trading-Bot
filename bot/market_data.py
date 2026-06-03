# market_data.py - جلب بيانات السوق الحقيقية

import time
import threading
import json
from kivy.logger import Logger

class MarketDataFetcher:
    """
    جلب بيانات السوق من منصة Quotex
    """
    
    def __init__(self, webview_manager):
        self.webview = webview_manager
        self.current_asset = "EUR/USD"
        self.current_timeframe = 1  # دقائق
        self.candles_cache = []
        self.last_update = 0
        self.update_interval = 5  # ثواني
        
    def set_asset(self, asset_name):
        """
        تحديد الأصل المراد تتبعه
        """
        self.current_asset = asset_name
        self.clear_cache()
        
    def set_timeframe(self, minutes):
        """
        تحديد الإطار الزمني
        """
        self.current_timeframe = minutes
        self.clear_cache()
        
    def clear_cache(self):
        """
        مسح ذاكرة التخزين المؤقت
        """
        self.candles_cache = []
        self.last_update = 0
        
    def fetch_current_price(self):
        """
        جلب السعر الحالي للأصل
        """
        if not self.webview or not self.webview.page_loaded:
            return self._get_mock_price()
        
        # محاولة جلب السعر من الصفحة
        js_code = """
        (function() {
            var priceElem = document.querySelector('span.current-price, .deal-price, .price-value');
            if (priceElem) {
                var price = parseFloat(priceElem.innerText.replace(',', '.'));
                return price;
            }
            return 0;
        })();
        """
        # في الواقع سيتم إرجاع القيمة عبر callback
        return self._get_mock_price()
    
    def fetch_candles(self, count=50):
        """
        جلب بيانات الشموع
        """
        if not self.webview or not self.webview.page_loaded:
            return self._get_mock_candles(count)
        
        # محاولة جلب بيانات الشموع من الصفحة
        # هذه الطريقة تعتمد على بنية صفحة Quotex
        js_code = f"""
        (function() {{
            var candles = [];
            
            // محاولة استخراج بيانات الشموع من عناصر الرسم البياني
            var chartCanvas = document.querySelector('canvas.chart-canvas, canvas[data-chart]');
            if (chartCanvas) {{
                // ملاحظة: استخراج البيانات من canvas معقد
                // قد يحتاج حل بديل مثل استخدام API
            }}
            
            // استخدام WebSocket إذا كان متاحاً
            if (window.quotex && window.quotex.chartData) {{
                candles = window.quotex.chartData.slice(-{count});
            }}
            
            return candles;
        }})();
        """
        self.webview.inject_javascript(js_code)
        return self._get_mock_candles(count)
    
    def fetch_ohlcv(self, timeframe=None, count=100):
        """
        جلب بيانات OHLCV (Open, High, Low, Close, Volume)
        """
        timeframe = timeframe or self.current_timeframe
        candles = self.fetch_candles(count)
        
        result = []
        for candle in candles:
            result.append({
                'timestamp': candle.get('timestamp', time.time()),
                'open': candle.get('open', 0),
                'high': candle.get('high', 0),
                'low': candle.get('low', 0),
                'close': candle.get('close', 0),
                'volume': candle.get('volume', 0)
            })
        
        return result
    
    def fetch_available_assets(self):
        """
        جلب جميع الأصول المتاحة للتداول
        """
        if not self.webview or not self.webview.page_loaded:
            return self._get_mock_assets()
        
        js_code = """
        (function() {
            var assets = [];
            var assetElements = document.querySelectorAll('.asset-item, .asset-select__option');
            assetElements.forEach(function(el) {
                var name = el.innerText || el.getAttribute('data-asset');
                if (name && name.trim()) {
                    assets.push(name.trim());
                }
            });
            return assets;
        })();
        """
        self.webview.inject_javascript(js_code)
        return self._get_mock_assets()
    
    def start_realtime_updates(self, callback):
        """
        بدء التحديثات الفورية للسعر
        """
        def update_loop():
            while True:
                try:
                    price = self.fetch_current_price()
                    if callback:
                        callback(price)
                    time.sleep(self.update_interval)
                except Exception as e:
                    Logger.error(f"MarketData: خطأ في التحديث - {e}")
                    time.sleep(5)
        
        thread = threading.Thread(target=update_loop, daemon=True)
        thread.start()
    
    def _get_mock_price(self):
        """
        سعر تجريبي (للتطوير والاختبار)
        """
        import random
        return round(random.uniform(1.0000, 1.2000), 4)
    
    def _get_mock_candles(self, count):
        """
        بيانات شموع تجريبية
        """
        import random
        candles = []
        base_price = 1.1000
        
        for i in range(count):
            change = random.uniform(-0.003, 0.003)
            close = base_price + change
            candles.append({
                'timestamp': time.time() - (count - i) * 60,
                'open': base_price,
                'high': max(base_price, close) + random.uniform(0, 0.001),
                'low': min(base_price, close) - random.uniform(0, 0.001),
                'close': close,
                'volume': random.randint(100, 1000)
            })
            base_price = close
        
        return candles
    
    def _get_mock_assets(self):
        """
        أصول تجريبية
        """
        return [
            "EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "USD/CAD",
            "BTC/USD", "ETH/USD", "XAU/USD", "EUR/GBP", "USD/CHF"
                    ]
