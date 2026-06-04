# bot/main.py - نسخة WebView النهائية

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle

# محاولة استيراد WebView (يعمل فقط على Android)
try:
    from android.webview import WebView
    from android.runnable import run_on_ui_thread
    WEBVIEW_AVAILABLE = True
except ImportError:
    WEBVIEW_AVAILABLE = False
    print("WebView not available on this platform")

import threading
import time

class QuotexBrowser(Widget):
    def __init__(self, **kwargs):
        super(QuotexBrowser, self).__init__(**kwargs)
        self.webview = None
        self.settings_visible = False
        self.bot_active = False
        
        # بناء الواجهة
        self.build_ui()
        
        # تحميل Quotex بعد ثانية من بدء التشغيل
        Clock.schedule_once(lambda dt: self.load_quotex(), 1)
    
    def build_ui(self):
        # خلفية سوداء
        with self.canvas.before:
            Color(0, 0, 0, 1)
            self.bg = Rectangle(size=self.size, pos=self.pos)
            self.bind(size=self._update_bg, pos=self._update_bg)
        
        # زر الإعدادات (ثلاث خطوط) - أعلى يسار
        self.settings_btn = Button(
            text="☰",
            size_hint=(0.1, 0.06),
            pos_hint={'x': 0.02, 'top': 0.98},
            background_color=(0.2, 0.2, 0.3, 1),
            font_size='25sp'
        )
        self.settings_btn.bind(on_press=self.toggle_settings)
        self.add_widget(self.settings_btn)
        
        # زر تنشيط البوت - أسفل يمين
        self.bot_btn = Button(
            text="▶ تنشيط",
            size_hint=(0.2, 0.07),
            pos_hint={'x': 0.75, 'y': 0.02},
            background_color=(0.2, 0.7, 0.2, 1),
            font_size='14sp'
        )
        self.bot_btn.bind(on_press=self.toggle_bot)
        self.add_widget(self.bot_btn)
        
        # لوحة الإعدادات (تظهر عند الضغط على زر الإعدادات)
        self.settings_panel = BoxLayout(
            orientation='vertical',
            size_hint=(0.9, 0.6),
            pos_hint={'x': 0.05, 'y': 0.2},
            spacing=8,
            padding=10
        )
        self.settings_panel.opacity = 0
        self.settings_panel.disabled = True
        
        # خلفية اللوحة
        with self.settings_panel.canvas.before:
            Color(0.1, 0.1, 0.15, 0.95)
            self.panel_bg = Rectangle(size=self.settings_panel.size, pos=self.settings_panel.pos)
            self.settings_panel.bind(size=self._update_panel_bg, pos=self._update_panel_bg)
        
        # عنوان اللوحة
        self.settings_panel.add_widget(Label(text="إعدادات البوت", size_hint=(1, 0.1), color=(1, 1, 1, 1)))
        
        # سبينر اختيار العملة
        self.pair_spinner = Spinner(
            text="اختر الزوج",
            values=["EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "BTC/USD"],
            size_hint=(1, 0.1)
        )
        self.settings_panel.add_widget(self.pair_spinner)
        
        # سبينر المبلغ
        self.amount_spinner = Spinner(
            text="المبلغ",
            values=["5", "10", "25", "50", "100", "250", "500"],
            size_hint=(1, 0.1)
        )
        self.settings_panel.add_widget(self.amount_spinner)
        
        # سبينر المدة
        self.timeframe_spinner = Spinner(
            text="مدة الشمعة",
            values=["1 دقيقة", "5 دقائق", "15 دقيقة", "30 دقيقة"],
            size_hint=(1, 0.1)
        )
        self.settings_panel.add_widget(self.timeframe_spinner)
        
        # سبينر نوع الحساب
        self.account_spinner = Spinner(
            text="نوع الحساب",
            values=["حساب تجريبي", "حساب حقيقي"],
            size_hint=(1, 0.1)
        )
        self.settings_panel.add_widget(self.account_spinner)
        
        # زر إغلاق اللوحة
        close_btn = Button(text="إغلاق", size_hint=(1, 0.08), background_color=(0.6, 0.2, 0.2, 1))
        close_btn.bind(on_press=self.toggle_settings)
        self.settings_panel.add_widget(close_btn)
        
        self.add_widget(self.settings_panel)
    
    def _update_bg(self, instance, value):
        self.bg.size = instance.size
        self.bg.pos = instance.pos
    
    def _update_panel_bg(self, instance, value):
        self.panel_bg.size = instance.size
        self.panel_bg.pos = instance.pos
    
    def load_quotex(self):
        """تحميل منصة Quotex في WebView"""
        if not WEBVIEW_AVAILABLE:
            self.show_popup("خطأ", "WebView غير متوفر على هذا الجهاز")
            return
        
        # إنشاء WebView يغطي الشاشة بالكامل
        self.webview = WebView(
            size_hint=(1, 1),
            pos_hint={'x': 0, 'y': 0}
        )
        self.add_widget(self.webview)
        # إرسال WebView إلى الخلف لظهور الأزرار فوقه
        self.remove_widget(self.webview)
        self.add_widget(self.webview, index=0)
        
        # تحميل المنصة
        self.webview.load_url("https://qxbroker.com")
        self.show_popup("متصفح Alking", "تم فتح المنصة. سجل دخولك يدوياً، ثم اضبط الإعدادات واضغط تنشيط.")
    
    def toggle_settings(self, instance):
        """إظهار/إخفاء لوحة الإعدادات"""
        self.settings_visible = not self.settings_visible
        if self.settings_visible:
            self.settings_panel.opacity = 1
            self.settings_panel.disabled = False
        else:
            self.settings_panel.opacity = 0
            self.settings_panel.disabled = True
    
    def toggle_bot(self, instance):
        """تشغيل/إيقاف البوت"""
        self.bot_active = not self.bot_active
        
        if self.bot_active:
            self.bot_btn.text = "⏸ إيقاف"
            self.bot_btn.background_color = (0.8, 0.2, 0.2, 1)
            self.show_popup("البوت", "تم تنشيط البوت. سيبدأ التداول بعد تحليل السوق.")
            # بدء البوت في thread منفصل
            threading.Thread(target=self.run_bot, daemon=True).start()
        else:
            self.bot_btn.text = "▶ تنشيط"
            self.bot_btn.background_color = (0.2, 0.7, 0.2, 1)
            self.show_popup("البوت", "تم إيقاف البوت")
    
    def run_bot(self):
        """تشغيل البوت (محاكاة حتى نضيف التحليل الحقيقي)"""
        win_streak = 0
        loss_streak = 0
        
        while self.bot_active:
            # هنا سنضيف كود التحليل الحقيقي لاحقاً
            # حالياً محاكاة 70% ربح
            import random
            signal = random.choice(["BUY", "SELL", "HOLD"])
            
            if signal != "HOLD":
                # تنفيذ صفقة في WebView
                if self.webview:
                    js_code = f"""
                    (function() {{
                        var btn = document.querySelector('button.{signal.lower()}-btn');
                        if (btn) btn.click();
                    }})();
                    """
                    self.webview.evaluate_javascript(js_code)
                
                # محاكاة النتيجة
                if random.randint(1, 100) <= 70:
                    win_streak += 1
                    loss_streak = 0
                else:
                    win_streak = 0
                    loss_streak += 1
                
                # شروط الإيقاف
                if win_streak >= 8:
                    self.stop_bot("تم تحقيق 8 صفقات ربح متتالية")
                    break
                if loss_streak >= 2:
                    self.stop_bot("تم تحقيق صفقتين خسارة متتالية")
                    break
            
            # انتظار 3 دقائق بين الصفقات
            for _ in range(180):
                if not self.bot_active:
                    break
                time.sleep(1)
    
    def stop_bot(self, reason):
        self.bot_active = False
        Clock.schedule_once(lambda dt: self.show_popup("توقف البوت", reason), 0)
        Clock.schedule_once(lambda dt: self.update_bot_button(), 0)
    
    def update_bot_button(self):
        self.bot_btn.text = "▶ تنشيط"
        self.bot_btn.background_color = (0.2, 0.7, 0.2, 1)
    
    def show_popup(self, title, message):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        layout.add_widget(Label(text=message, color=(1, 1, 1, 1)))
        btn = Button(text="إغلاق", size_hint=(1, 0.3))
        layout.add_widget(btn)
        popup = Popup(title=title, content=layout, size_hint=(0.8, 0.4))
        btn.bind(on_press=popup.dismiss)
        popup.open()

class AlkingApp(App):
    def build(self):
        Window.clearcolor = (0, 0, 0, 1)
        return QuotexBrowser()

if __name__ == "__main__":
    AlkingApp().run()
