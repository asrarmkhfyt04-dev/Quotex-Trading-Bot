# main.py - معدل للعمل على Android

import time
import logging
import threading
from kivy.clock import Clock
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# متغيرات عالمية للتطبيق
trading_active = False
current_balance = 0
trade_count = 0
win_count = 0
loss_count = 0

class AlkingApp(App):
    def build(self):
        self.title = "Alking"
        Window.size = (360, 640)
        
        # الواجهة الرئيسية
        self.main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # عنوان التطبيق
        title_label = Label(text="[b]ALKING TRADING BOT[/b]", markup=True, size_hint=(1, 0.1), font_size='20sp')
        self.main_layout.add_widget(title_label)
        
        # حقل إيميل
        self.email_input = TextInput(hint_text="البريد الإلكتروني", multiline=False, size_hint=(1, 0.08))
        self.main_layout.add_widget(self.email_input)
        
        # حقل كلمة سر
        self.password_input = TextInput(hint_text="كلمة السر", password=True, multiline=False, size_hint=(1, 0.08))
        self.main_layout.add_widget(self.password_input)
        
        # زر تسجيل الدخول
        login_btn = Button(text="تسجيل الدخول", size_hint=(1, 0.08), background_color=(0.2, 0.6, 0.2, 1))
        login_btn.bind(on_press=self.login)
        self.main_layout.add_widget(login_btn)
        
        # سبينر اختيار الزوج (العملة)
        self.pair_spinner = Spinner(
            text="اختر الزوج",
            values=["EUR/USD", "GBP/USD", "USD/JPY", "BTC/USD", "ETH/USD"],
            size_hint=(1, 0.08)
        )
        self.main_layout.add_widget(self.pair_spinner)
        
        # سبينر اختيار المبلغ
        self.amount_spinner = Spinner(
            text="المبلغ",
            values=["10", "25", "50", "100", "250", "500"],
            size_hint=(1, 0.08)
        )
        self.main_layout.add_widget(self.amount_spinner)
        
        # سبينر اختيار مدة الشمعة
        self.timeframe_spinner = Spinner(
            text="مدة الشمعة",
            values=["1 دقيقة", "5 دقائق", "15 دقيقة", "30 دقيقة", "1 ساعة"],
            size_hint=(1, 0.08)
        )
        self.main_layout.add_widget(self.timeframe_spinner)
        
        # سبينر اختيار حساب حقيقي/تجريبي
        self.account_spinner = Spinner(
            text="نوع الحساب",
            values=["حساب تجريبي", "حساب حقيقي"],
            size_hint=(1, 0.08)
        )
        self.main_layout.add_widget(self.account_spinner)
        
        # زر تنشيط البوت
        self.activate_btn = Button(text="▶ تنشيط البوت", size_hint=(1, 0.1), background_color=(0.2, 0.2, 0.8, 1))
        self.activate_btn.bind(on_press=self.toggle_bot)
        self.main_layout.add_widget(self.activate_btn)
        
        # منطقة عرض الحالة والإحصائيات
        self.status_label = Label(text="[b]الحالة:[/b] غير نشط\n[b]الرصيد:[/b] 0\n[b]صفقات رابحة:[/b] 0\n[b]صفقات خاسرة:[/b] 0", 
                                   markup=True, size_hint=(1, 0.25), valign='top')
        self.main_layout.add_widget(self.status_label)
        
        return self.main_layout
    
    def login(self, instance):
        email = self.email_input.text
        password = self.password_input.text
        
        if email and password:
            self.status_label.text = f"[b]الحالة:[/b] جاري تسجيل الدخول...\n[b]الرصيد:[/b] 0\n[b]صفقات رابحة:[/b] 0\n[b]صفقات خاسرة:[/b] 0"
            # هنا سيتم إضافة كود تسجيل الدخول الفعلي للمنصة
            Clock.schedule_once(lambda dt: self.show_popup("نجاح", f"تم تسجيل الدخول بنجاح\nمرحباً {email}"), 1)
        else:
            self.show_popup("خطأ", "الرجاء إدخال البريد الإلكتروني وكلمة السر")
    
    def toggle_bot(self, instance):
        global trading_active
        trading_active = not trading_active
        
        if trading_active:
            self.activate_btn.text = "⏸ إيقاف البوت"
            self.activate_btn.background_color = (0.8, 0.2, 0.2, 1)
            self.status_label.text = f"[b]الحالة:[/b] نشط - يعمل...\n[b]الرصيد:[/b] {current_balance}\n[b]صفقات رابحة:[/b] {win_count}\n[b]صفقات خاسرة:[/b] {loss_count}"
            # بدء البوت في thread منفصل
            threading.Thread(target=self.run_bot, daemon=True).start()
        else:
            self.activate_btn.text = "▶ تنشيط البوت"
            self.activate_btn.background_color = (0.2, 0.2, 0.8, 1)
            self.status_label.text = f"[b]الحالة:[/b] غير نشط\n[b]الرصيد:[/b] {current_balance}\n[b]صفقات رابحة:[/b] {win_count}\n[b]صفقات خاسرة:[/b] {loss_count}"
    
    def run_bot(self):
        global trade_count, win_count, loss_count, current_balance
        
        while trading_active:
            logging.info("تحليل السوق...")
            
            # هنا سيتم إضافة كود التحليل الفعلي والتداول
            # حالياً هو نموذج تجريبي
            
            # محاكاة تحليل وإشارة
            signal = self.analyze_market()
            
            if signal == "BUY":
                self.execute_trade("UP")
            elif signal == "SELL":
                self.execute_trade("DOWN")
            
            # الانتظار بين 3-5 دقائق
            for i in range(180):  # 3 دقائق
                if not trading_active:
                    break
                time.sleep(1)
    
    def analyze_market(self):
        """تحليل السوق وإرجاع إشارة BUY/SELL/HOLD"""
        # هذا كود تحليل بسيط - سيتم تطويره لاحقاً
        import random
        # محاكاة تحليل 70% دقة
        rand = random.randint(1, 100)
        if rand <= 35:
            return "BUY"
        elif rand <= 70:
            return "SELL"
        else:
            return "HOLD"
    
    def execute_trade(self, direction):
        global trade_count, win_count, loss_count, current_balance
        
        trade_count += 1
        amount = int(self.amount_spinner.text)
        
        # محاكاة نتيجة الصفقة (70% ربح)
        import random
        is_win = random.randint(1, 100) <= 70
        
        if is_win:
            win_count += 1
            current_balance += amount * 0.8
            result = "رابحة ✅"
        else:
            loss_count += 1
            current_balance -= amount
            result = "خاسرة ❌"
        
        # تحديث واجهة المستخدم
        Clock.schedule_once(lambda dt: self.update_stats(), 0)
        
        logging.info(f"صفقة {trade_count}: {direction} - {result}")
        
        # إيقاف البوت بعد 8 صفقات ربح أو صفقتين خسارة
        if win_count >= 8:
            Clock.schedule_once(lambda dt: self.stop_bot("تم تحقيق 8 صفقات ربح متتالية"), 0)
        elif loss_count >= 2:
            Clock.schedule_once(lambda dt: self.stop_bot("تم تحقيق صفقتين خسارة متتالية"), 0)
    
    def update_stats(self):
        self.status_label.text = f"[b]الحالة:[/b] {'نشط' if trading_active else 'غير نشط'}\n[b]الرصيد:[/b] {current_balance:.2f}\n[b]صفقات رابحة:[/b] {win_count}\n[b]صفقات خاسرة:[/b] {loss_count}"
    
    def stop_bot(self, reason):
        global trading_active
        trading_active = False
        self.activate_btn.text = "▶ تنشيط البوت"
        self.activate_btn.background_color = (0.2, 0.2, 0.8, 1)
        self.show_popup("توقف البوت", f"السبب: {reason}")
        self.update_stats()
    
    def show_popup(self, title, message):
        popup_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        popup_label = Label(text=message, markup=True)
        close_btn = Button(text="إغلاق", size_hint=(1, 0.3))
        popup_layout.add_widget(popup_label)
        popup_layout.add_widget(close_btn)
        popup = Popup(title=title, content=popup_layout, size_hint=(0.8, 0.4))
        close_btn.bind(on_press=popup.dismiss)
        popup.open()

if __name__ == "__main__":
    AlkingApp().run()
