# webview_manager.py - إدارة WebView للربط مع Quotex

import threading
import time
import json
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.logger import Logger

# محاولة استيراد WebView (يختلف حسب المنصة)
try:
    from android.runnable import run_on_ui_thread
    from jnius import autoclass, PythonJavaClass, java_method
    WEBVIEW_AVAILABLE = True
except ImportError:
    WEBVIEW_AVAILABLE = False
    Logger.warning("WebView: غير متوفر على هذه المنصة")

class QuotexWebViewManager:
    """
    مدير WebView للتفاعل مع منصة Quotex
    """
    
    def __init__(self):
        self.webview = None
        self.is_ready = False
        self.is_logged_in = False
        self.current_balance = 0
        self.available_assets = []
        self.page_loaded = False
        
    def init_webview(self, layout):
        """
        تهيئة WebView داخل التطبيق
        """
        if not WEBVIEW_AVAILABLE:
            Logger.warning("WebView: غير متوفر، سيتم استخدام وضع المحاكاة")
            return False
        
        try:
            # كود تهيئة WebView للأندرويد
            WebView = autoclass('android.webkit.WebView')
            WebViewClient = autoclass('android.webkit.WebViewClient')
            WebChromeClient = autoclass('android.webkit.WebChromeClient')
            Activity = autoclass('org.kivy.android.PythonActivity')
            
            self.webview = WebView(Activity.getRootView().getContext())
            self.webview.getSettings().setJavaScriptEnabled(True)
            self.webview.getSettings().setDomStorageEnabled(True)
            self.webview.getSettings().setLoadWithOverviewMode(True)
            self.webview.getSettings().setUseWideViewPort(True)
            
            # إضافة WebView إلى التخطيط
            layout.add_widget(self.webview)
            
            # تعيين WebViewClient
            self.webview.setWebViewClient(WebViewClient())
            self.webview.setWebChromeClient(WebChromeClient())
            
            return True
        except Exception as e:
            Logger.error(f"WebView: فشل التهيئة - {e}")
            return False
    
    def load_url(self, url):
        """
        تحميل رابط المنصة
        """
        if self.webview:
            self.webview.loadUrl(url)
            self.page_loaded = True
            return True
        return False
    
    def inject_javascript(self, js_code):
        """
        حقن كود JavaScript في الصفحة
        """
        if self.webview and self.page_loaded:
            self.webview.evaluateJavascript(js_code, None)
            return True
        return False
    
    def login(self, email, password):
        """
        تسجيل الدخول إلى Quotex عبر حقن JavaScript
        """
        js_code = f"""
        (function() {{
            // انتظار تحميل الصفحة
            setTimeout(function() {{
                // إدخال البريد الإلكتروني
                var emailInput = document.querySelector('input[name="email"]');
                if (emailInput) {{
                    emailInput.value = '{email}';
                    emailInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                }}
                
                // إدخال كلمة السر
                var passInput = document.querySelector('input[name="password"]');
                if (passInput) {{
                    passInput.value = '{password}';
                    passInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                }}
                
                // الضغط على زر تسجيل الدخول
                var loginBtn = document.querySelector('button[type="submit"]');
                if (loginBtn) {{
                    loginBtn.click();
                }}
                
                // إرجاع النتيجة
                return {{ success: true }};
            }}, 2000);
        }})();
        """
        self.inject_javascript(js_code)
        self.is_logged_in = True
        return True
    
    def switch_to_demo(self):
        """
        التحويل إلى الحساب التجريبي
        """
        js_code = """
        (function() {
            // فتح قائمة المستخدم
            var menuBtn = document.querySelector('div.usermenu__info-wrapper');
            if (menuBtn) menuBtn.click();
            
            setTimeout(function() {
                // الضغط على الحساب التجريبي
                var demoLink = document.querySelector('a.usermenu__select-name[href*="demo"]');
                if (demoLink) demoLink.click();
                
                setTimeout(function() {
                    // إغلاق النافذة المنبثقة
                    var closeBtn = document.querySelector('button.modal-account-type-changed__body-button');
                    if (closeBtn) closeBtn.click();
                }, 1000);
            }, 500);
        })();
        """
        self.inject_javascript(js_code)
        return True
    
    def get_balance(self):
        """
        الحصول على الرصيد من الصفحة
        """
        js_code = """
        (function() {
            var balanceElem = document.querySelector('div.usermenu__info-balance');
            if (balanceElem) {
                var balance = balanceElem.innerText.replace('$', '').replace(',', '');
                return parseFloat(balance);
            }
            return 0;
        })();
        """
        # هذا سيعيد القيمة عبر callback
        self.inject_javascript(js_code)
        return self.current_balance
    
    def get_available_assets(self):
        """
        جلب قائمة الأصول (العملات) المتاحة من المنصة
        """
        js_code = """
        (function() {
            var assets = [];
            var assetElements = document.querySelectorAll('.asset-item, .asset-select__option, [data-asset]');
            assetElements.forEach(function(elem) {
                var assetName = elem.innerText || elem.getAttribute('data-asset');
                if (assetName && assetName.trim()) {
                    assets.push(assetName.trim());
                }
            });
            return assets;
        })();
        """
        self.inject_javascript(js_code)
        return self.available_assets
    
    def select_asset(self, asset_name):
        """
        اختيار أصل (عملة) معينة
        """
        js_code = f"""
        (function() {{
            // فتح قائمة الأصول
            var assetBtn = document.querySelector('button.asset-select__button');
            if (assetBtn) assetBtn.click();
            
            setTimeout(function() {{
                // اختيار الأصل المطلوب
                var assetElement = Array.from(document.querySelectorAll('.asset-item, .asset-select__option')).find(
                    el => el.innerText.includes('{asset_name}')
                );
                if (assetElement) assetElement.click();
            }}, 500);
        }})();
        """
        self.inject_javascript(js_code)
        return True
    
    def set_investment_amount(self, amount):
        """
        تحديد مبلغ الاستثمار
        """
        js_code = f"""
        (function() {{
            var investInput = document.querySelector('input.input-control__input');
            if (investInput) {{
                investInput.value = '{amount}';
                investInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                investInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
            }}
        }})();
        """
        self.inject_javascript(js_code)
        return True
    
    def set_timeframe(self, minutes):
        """
        تحديد مدة الشمعة
        """
        # تحويل الدقائق إلى تنسيق HH:MM:SS
        time_str = f"00:{minutes:02d}:00"
        js_code = f"""
        (function() {{
            var timeBtns = document.querySelectorAll('.time-selector__item, .duration-selector__item');
            timeBtns.forEach(function(btn) {{
                if (btn.innerText.includes('{minutes}') || btn.innerText.includes('{time_str}')) {{
                    btn.click();
                }}
            }});
        }})();
        """
        self.inject_javascript(js_code)
        return True
    
    def place_trade(self, direction):
        """
        تنفيذ صفقة (UP/DOWN)
        """
        if direction.upper() == "UP":
            js_code = """
            (function() {
                var upBtn = document.querySelector('button.call-btn, button.button--success');
                if (upBtn) upBtn.click();
            })();
            """
        else:
            js_code = """
            (function() {
                var downBtn = document.querySelector('button.put-btn, button.button--danger');
                if (downBtn) downBtn.click();
            })();
            """
        self.inject_javascript(js_code)
        return True
    
    def get_candlestick_data(self, asset, timeframe):
        """
        جلب بيانات الشموع من المنصة
        """
        # هذا الكود يحتاج API من المنصة أو scraping متقدم
        js_code = f"""
        (function() {{
            // محاولة جلب بيانات الشموع من عناصر الصفحة
            var candles = [];
            var chartElements = document.querySelectorAll('.candle, .chart-candle, [data-candle]');
            chartElements.forEach(function(elem) {{
                var high = parseFloat(elem.getAttribute('data-high') || 0);
                var low = parseFloat(elem.getAttribute('data-low') || 0);
                var open = parseFloat(elem.getAttribute('data-open') || 0);
                var close = parseFloat(elem.getAttribute('data-close') || 0);
                if (high && low && open && close) {{
                    candles.push({{ high: high, low: low, open: open, close: close }});
                }}
            }});
            return candles;
        }})();
        """
        self.inject_javascript(js_code)
        # في الواقع سيتم إرجاع البيانات عبر callback
        return []
    
    def wait_for_page_load(self, timeout=30):
        """
        انتظار تحميل الصفحة بالكامل
        """
        import time
        start = time.time()
        while not self.page_loaded and time.time() - start < timeout:
            time.sleep(0.5)
        return self.page_loaded
    
    def close(self):
        """
        إغلاق WebView وتحرير الموارد
        """
        if self.webview:
            self.webview.stopLoading()
            self.webview.destroy()
            self.webview = None
        self.is_ready = False
        self.is_logged_in = False
