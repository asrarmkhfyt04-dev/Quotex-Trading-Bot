# app.py - نسخة معدلة بالكامل للعمل على Android

"""
هذا الملف هو المدخل الرئيسي للتطبيق على Android
تم تعديله ليعمل مع Kivy بدلاً من Streamlit
"""

from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp

import threading
import time
import logging

# إعداد التسجيل
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# استيراد الوحدات المحلية
from config import *
from strategy import TradingStrategy
from risk_management import RiskManager
from trade_executor import TradeExecutor

# متغيرات عالمية
trading_active = False
trade_thread = None
win_streak = 0
loss_streak = 0
total_wins = 0
total_losses = 0
current_balance = 10000.0
trade_count = 0

# واجهة المستخدم الرئيسية
class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.build_ui()
        
    def build_ui(self):
        # التخطيط الرئيسي
        layout = FloatLayout()
        
        # خلفية التطبيق
        from kivy.graphics import Color, Rectangle
        with layout.canvas.before:
            Color(0.05, 0.05, 0.1, 1)  # لون خلفية داكن
            self.bg = Rectangle(size=Window.size, pos=layout.pos)
            layout.bind(size=self._update_bg, pos=self._update_bg)
        
        # عنوان التطبيق
        title = Label(
            text="[b]ALKING[/b]",
            markup=True,
            font_size='30sp',
            color=(0.2, 0.8, 0.2, 1),
            size_hint=(1, 0.08),
            pos_hint={'x': 0, 'top': 1}
        )
        layout.add_widget(title)
        
        # حقل البريد الإلكتروني
        self.email_input = TextInput(
            hint_text="البريد الإلكتروني",
            multiline=False,
            size_hint=(0.9, 0.07),
            pos_hint={'x': 0.05, 'top': 0.9},
            background_color=(0.2, 0.2, 0.3, 1),
            foreground_color=(1, 1, 1, 1),
            hint_text_color=(0.7, 0.7, 0.7, 1)
        )
        layout.add_widget(self.email_input)
        
        # حقل كلمة السر
        self.password_input = TextInput(
            hint_text="كلمة السر",
            password=True,
            multiline=False,
            size_hint=(0.9, 0.07),
            pos_hint={'x': 0.05, 'top': 0.82},
            background_color=(0.2, 0.2, 0.3, 1),
            foreground_color=(1, 1, 1, 1),
            hint_text_color=(0.7, 0.7, 0.7, 1)
        )
        layout.add_widget(self.password_input)
        
        # زر تسجيل الدخول
        self.login_btn = Button(
            text="تسجيل الدخول",
            size_hint=(0.9, 0.07),
            pos_hint={'x': 0.05, 'top': 0.74},
            background_color=(0.2, 0.6, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        self.login_btn.bind(on_press=self.login)
        layout.add_widget(self.login_btn)
        
        # سبينر اختيار الزوج
        self.pair_spinner = Spinner(
            text="اختر الزوج",
            values=["EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "BTC/USD", "ETH/USD"],
            size_hint=(0.9, 0.07),
            pos_hint={'x': 0.05, 'top': 0.66},
            background_color=(0.2, 0.2, 0.3, 1),
            color=(1, 1, 1, 1)
        )
        layout.add_widget(self.pair_spinner)
        
        # سبينر اختيار المبلغ
        self.amount_spinner = Spinner(
            text="المبلغ",
            values=["10", "25", "50", "100", "250", "500", "1000"],
            size_hint=(0.9, 0.07),
            pos_hint={'x': 0.05, 'top': 0.58},
            background_color=(0.2, 0.2, 0.3, 1),
            color=(1, 1, 1, 1)
        )
        layout.add_widget(self.amount_spinner)
        
        # سبينر مدة الشمعة
        self.timeframe_spinner = Spinner(
            text="مدة الشمعة",
            values=["1 دقيقة", "5 دقائق", "15 دقيقة", "30 دقيقة", "1 ساعة"],
            size_hint=(0.9, 0.07),
            pos_hint={'x': 0.05, 'top': 0.50},
            background_color=(0.2, 0.2, 0.3, 1),
            color=(1, 1, 1, 1)
        )
        layout.add_widget(self.timeframe_spinner)
        
        # سبينر نوع الحساب
        self.account_spinner = Spinner(
            text="نوع الحساب",
            values=["حساب تجريبي", "حساب حقيقي"],
            size_hint=(0.9, 0.07),
            pos_hint={'x': 0.05, 'top': 0.42},
            background_color=(0.2, 0.2, 0.3, 1),
            color=(1, 1, 1, 1)
        )
        layout.add_widget(self.account_spinner)
        
        # زر تنشيط البوت
        self.activate_btn = Button(
            text="▶ تنشيط البوت",
            size_hint=(0.9, 0.08),
            pos_hint={'x': 0.05, 'top': 0.33},
            background_color=(0.2, 0.2, 0.8, 1),
            color=(1, 1, 1, 1)
        )
        self.activate_btn.bind(on_press=self.toggle_bot)
        layout.add_widget(self.activate_btn)
        
        # عرض الحالة والإحصائيات
        self.status_label = Label(
            text="[b]الحالة:[/b] غير نشط\n[b]الرصيد:[/b] 0\n[b]الأرباح:[/b] 0\n[b]الخسائر:[/b] 0\n[b]أرباح متتالية:[/b] 0",
            markup=True,
            size_hint=(0.9, 0.2),
            pos_hint={'x': 0.05, 'top': 0.30},
            halign='left',
            valign='top',
            color=(0.9, 0.9, 0.9, 1)
        )
        self.status_label.bind(size=self.status_label.setter('text_size'))
        layout.add_widget(self.status_label)
        
        self.add_widget(layout)
    
    def _update_bg(self, instance, value):
        self.bg.size = instance.size
        self.bg.pos = instance.pos
    
    def login(self, instance):
        email = self.email_input.text
        password = self.password_input.text
        
        if email and password:
            self.status_label.text = "[b]الحالة:[/b] جاري تسجيل الدخول...\n[b]الرصيد:[/b] 0\n[b]الأرباح:[/b] 0\n[b]الخسائر:[/b] 0\n[b]أرباح متتالية:[/b] 0"
            Clock.schedule_once(lambda dt: self.show_popup("نجاح", f"تم تسجيل الدخول بنجاح"), 1)
        else:
            self.show_popup("خطأ", "الرجاء إدخال البريد الإلكتروني وكلمة السر")
    
    def toggle_bot(self, instance):
        global trading_active, win_streak, loss_streak, total_wins, total_losses, trade_count, current_balance
        
        if not self.email_input.text or not self.password_input.text:
            self.show_popup("خطأ", "الرجاء تسجيل الدخول أولاً")
            return
        
        trading_active = not trading_active
        
        if trading_active:
            self.activate_btn.text = "⏸ إيقاف البوت"
            self.activate_btn.background_color = (0.8, 0.2, 0.2, 1)
            
            # إعادة ضبط المتغيرات
            win_streak = 0
            loss_streak = 0
            total_wins = 0
            total_losses = 0
            trade_count = 0
            current_balance = 10000.0 if self.account_spinner.text == "حساب تجريبي" else 1000.0
            
            self.update_status()
            
            # بدء البوت في thread منفصل
            self.trade_thread = threading.Thread(target=self.run_bot, daemon=True)
            self.trade_thread.start()
        else:
            self.activate_btn.text = "▶ تنشيط البوت"
            self.activate_btn.background_color = (0.2, 0.2, 0.8, 1)
            self.update_status()
    
    def run_bot(self):
        global trading_active, win_streak, loss_streak, total_wins, total_losses, trade_count, current_balance
        
        # تهيئة المكونات
        strategy = TradingStrategy()
        risk_manager = RiskManager()
        executor = TradeExecutor()
        
        # محاكاة تسجيل الدخول للمنصة
        executor.login(self.email_input.text, self.password_input.text, 
                      self.account_spinner.text == "حساب تجريبي")
        
        while trading_active:
            try:
                # تحديث الرصيد
                current_balance = executor.get_account_balance()
                
                # جلب بيانات السوق
                market_data = executor.fetch_market_data()
                
                # تحليل السوق
                signal = strategy.generate_signal(market_data)
                confidence = strategy.get_signal_confidence(market_data)
                
                if signal != "HOLD" and confidence >= 70:
                    # حساب المبلغ المناسب
                    amount = float(self.amount_spinner.text)
                    if amount > current_balance:
                        amount = current_balance * 0.02
                    
                    executor.set_investment_amount(amount)
                    
                    # اختيار الزوج
                    executor.select_asset(self.pair_spinner.text)
                    
                    # تنفيذ الصفقة
                    result = executor.place_trade(signal)
                    
                    if result['win']:
                        win_streak += 1
                        loss_streak = 0
                        total_wins += 1
                        current_balance += result.get('profit', amount * 0.8)
                        trade_result = "رابحة ✅"
                    else:
                        win_streak = 0
                        loss_streak += 1
                        total_losses += 1
                        current_balance -= amount
                        trade_result = "خاسرة ❌"
                    
                    trade_count += 1
                    
                    # تحديث الواجهة
                    Clock.schedule_once(lambda dt: self.update_status(), 0)
                    
                    logging.info(f"صفقة {trade_count}: {signal} - {trade_result}")
                    
                    # التحقق من شروط الإيقاف
                    if win_streak >= 8:
                        Clock.schedule_once(lambda dt: self.stop_bot("تم تحقيق 8 صفقات ربح متتالية"), 0)
                        break
                    elif loss_streak >= 2:
                        Clock.schedule_once(lambda dt: self.stop_bot("تم تحقيق صفقتين خسارة متتالية"), 0)
                        break
                
                # انتظار بين الصفقات (3-5 دقائق)
                for i in range(180):  # 3 دقائق
                    if not trading_active:
                        break
                    time.sleep(1)
                
            except Exception as e:
                logging.error(f"خطأ: {e}")
                time.sleep(30)
        
        executor.close()
    
    def update_status(self):
        global trading_active, current_balance, total_wins, total_losses, win_streak
        
        status_text = f"[b]الحالة:[/b] {'نشط ✓' if trading_active else 'غير نشط'}\n"
        status_text += f"[b]الرصيد:[/b] ${current_balance:.2f}\n"
        status_text += f"[b]الأرباح:[/b] {total_wins}\n"
        status_text += f"[b]الخسائر:[/b] {total_losses}\n"
        status_text += f"[b]أرباح متتالية:[/b] {win_streak}"
        
        self.status_label.text = status_text
    
    def stop_bot(self, reason):
        global trading_active
        trading_active = False
        self.activate_btn.text = "▶ تنشيط البوت"
        self.activate_btn.background_color = (0.2, 0.2, 0.8, 1)
        self.show_popup("توقف البوت", reason)
        self.update_status()
    
    def show_popup(self, title, message):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        layout.add_widget(Label(text=message, markup=True))
        btn = Button(text="إغلاق", size_hint=(1, 0.3))
        layout.add_widget(btn)
        popup = Popup(title=title, content=layout, size_hint=(0.8, 0.4))
        btn.bind(on_press=popup.dismiss)
        popup.open()


# مدير الشاشات
class AlkingApp(ScreenManager):
    def __init__(self, **kwargs):
        super(AlkingApp, self).__init__(**kwargs)
        self.add_widget(MainScreen(name='main'))


# نقطة الدخول الرئيسية
if __name__ == '__main__':
    from kivy.base import runTouchApp
    runTouchApp(AlkingApp())
