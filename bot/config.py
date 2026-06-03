# config.py - معدل للعمل على Android

import os

# بيانات تسجيل الدخول (سيتم إدخالها من المستخدم عبر الواجهة)
QUOTEX_USERNAME = ""
QUOTEX_PASSWORD = ""
USE_DEMO = True

# الزوج الافتراضي (سيتم اختياره من المستخدم)
ASSET_NAME = "EUR/USD"

# إعدادات المؤشرات الفنية
RSI_THRESHOLD = 30
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

# إعدادات المخاطرة والتداول
TRADE_AMOUNT = 10.0  # المبلغ الافتراضي بالدولار
BOLLINGER_PERIOD = 20
BOLLINGER_STD_DEV = 2.0

# إعدادات البوت
MAX_WIN_STREAK = 8      # وقف بعد 8 صفقات ربح
MAX_LOSS_STREAK = 2     # وقف بعد صفقتين خسارة
SLEEP_BETWEEN_TRADES = 180  # 3 دقائق بين كل صفقة (بالثواني)

# إعدادات المنصة
PLATFORM_URL = "https://qxbroker.com"
WEBVIEW_LOAD_TIMEOUT = 30
