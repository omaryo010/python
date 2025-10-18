import os
from dotenv import load_dotenv

load_dotenv()

# ⚠️ تحذير: هذا البرنامج يعمل على حساب حقيقي - تأكد من الاختبار على testnet أولاً
# WARNING: This program operates on a LIVE account - test on testnet first!

# ==================== إعدادات API بينانس ====================
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', 'your_api_key_here')
BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET', 'your_api_secret_here')

# استخدم testnet للاختبار - غير هذا إلى True للاختبار
TESTNET = False  # قيمة False تعني الحساب الحقيقي!

# ==================== إعدادات التداول ====================
TRADING_PAIR = 'BTCUSDT'  # العملة المراد التداول عليها
TIMEFRAME = '5m'  # الإطار الزمني: 5 دقائق
TRADE_AMOUNT_USDT = 10  # قيمة الصفقة بالدولار

# ==================== إعدادات الدعم والمقاومة ====================
LOOKBACK_CANDLES = 50  # عدد الشموع للنظر للخلف لحساب الدعم والمقاومة
SUPPORT_RESISTANCE_THRESHOLD = 0.02  # نسبة القرب من الدعم/المقاومة (2%)
TRENDLINE_LOOKBACK = 20  # عدد الشموع لحساب خطوط الترند

# ==================== إعدادات إدارة المخاطر ====================
STOP_LOSS_PERCENTAGE = 2.0  # وقف الخسارة (%)
TAKE_PROFIT_PERCENTAGE = 3.0  # جني الربح (%)
MAX_OPEN_POSITIONS = 3  # الحد الأقصى للصفقات المفتوحة

# ==================== إعدادات التطبيق ====================
CHECK_INTERVAL = 60  # فترة الفحص بالثواني (كل دقيقة واحدة)
LOG_LEVEL = 'INFO'  # مستوى السجل (DEBUG, INFO, WARNING, ERROR)
LOG_FILE = 'trading_bot.log'  # اسم ملف السجل

# ==================== إعدادات البيانات ====================
CANDLES_TO_FETCH = 100  # عدد الشموع المراد جلبها من التاريخ
