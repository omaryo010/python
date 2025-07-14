import requests
import pandas as pd
import ta
import threading
import time
import sqlite3
import traceback
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.uix.spinner import Spinner
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, RoundedRectangle
from kivy.clock import Clock

import arabic_reshaper
from bidi.algorithm import get_display

# اسم الخط المخصص
ARABIC_FONT_PATH = "AQEEQSANSPRO-Light.otf.ttf"

Window.clearcolor = (0.08, 0.10, 0.18, 1)

CRYPTO_SYMBOLS = [
    "DOGEUSDT", "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT",
    "ADAUSDT", "TRXUSDT", "XRPUSDT", "MATICUSDT", "SHIBUSDT"
]
INTERVALS = [
    "1m", "5m", "15m", "30m", "1h", "4h", "1d"
]
INTERVAL_LABELS = {
    "1m": "1 دقيقة",
    "5m": "5 دقائق",
    "15m": "15 دقيقة",
    "30m": "30 دقيقة",
    "1h": "1 ساعة",
    "4h": "4 ساعات",
    "1d": "1 يوم"
}
DB_FILE = "crypto_history.db"

def ar(text):
    """تشكيل وعكس النص العربي ليظهر صحيحاً في Kivy."""
    if not isinstance(text, str):
        return text
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)

class TradingSimulator:
    def __init__(self, initial_balance=1000.0):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.position = 0.0
        self.entry_price = None
        self.trades = []
        self.num_wins = 0
        self.num_losses = 0

    def enter_trade(self, price):
        if self.position == 0.0 and self.balance > 0:
            self.position = self.balance / price
            self.entry_price = price
            self.balance = 0.0

    def exit_trade(self, price):
        if self.position > 0.0:
            exit_balance = self.position * price
            profit = exit_balance - (self.entry_price * self.position)
            if profit > 0:
                self.num_wins += 1
            else:
                self.num_losses += 1
            self.trades.append({
                'entry': self.entry_price,
                'exit': price,
                'profit': profit
            })
            self.balance = exit_balance
            self.position = 0.0
            self.entry_price = None

    def get_performance(self):
        total_profit = sum(t['profit'] for t in self.trades)
        return {
            'balance': self.balance,
            'open_position': self.position,
            'entry_price': self.entry_price,
            'num_trades': len(self.trades),
            'wins': self.num_wins,
            'losses': self.num_losses,
            'total_profit': total_profit
        }

    def get_trades_log(self):
        lines = []
        for idx, t in enumerate(self.trades):
            status = ar("[color=27ae60]ربح[/color]") if t['profit'] > 0 else ar("[color=ea4335]خسارة[/color]")
            lines.append(ar(f"صفقة {idx+1}: دخول={t['entry']:.6f}, خروج={t['exit']:.6f}, ربح={t['profit']:.2f} {status}"))
        return "\n".join(lines) if lines else ar("لا صفقات بعد.")

def create_database():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS history (
            symbol TEXT,
            interval TEXT,
            open_time INTEGER PRIMARY KEY,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume REAL
        )
    ''')
    conn.commit()
    conn.close()

def get_last_open_time(symbol, interval):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT MAX(open_time) FROM history WHERE symbol=? AND interval=?', (symbol, interval))
    result = c.fetchone()
    conn.close()
    return result[0] if result and result[0] else None

def fetch_binance_klines(symbol, interval, start_time=None, end_time=None, limit=1000):
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    if start_time:
        params["startTime"] = int(start_time)
    if end_time:
        params["endTime"] = int(end_time)
    response = requests.get(url, params=params)
    data = response.json()
    columns = [
        'open_time', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base', 'taker_buy_quote', 'ignore'
    ]
    df = pd.DataFrame(data, columns=columns)
    for col in ['open', 'high', 'low', 'close', 'volume']:
        df[col] = df[col].astype(float)
    return df

def save_history(symbol, interval, df):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    for _, row in df.iterrows():
        c.execute('''
            INSERT OR IGNORE INTO history (symbol, interval, open_time, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (symbol, interval, int(row['open_time']), row['open'], row['high'], row['low'], row['close'], row['volume']))
    conn.commit()
    conn.close()

def sync_full_history(symbol, interval):
    create_database()
    last_open_time = get_last_open_time(symbol, interval)
    while True:
        start_time = last_open_time + 1 if last_open_time else None
        df = fetch_binance_klines(symbol, interval, start_time=start_time, limit=1000)
        if df.empty:
            break
        save_history(symbol, interval, df)
        last_open_time = int(df['open_time'].max())
        if len(df) < 1000:
            break

def update_latest_price(symbol, interval):
    df = fetch_binance_klines(symbol, interval, limit=2)
    if not df.empty:
        save_history(symbol, interval, df.tail(1))

def load_history(symbol, interval, limit=100):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        SELECT open_time, open, high, low, close, volume FROM history
        WHERE symbol=? AND interval=?
        ORDER BY open_time DESC LIMIT ?
    ''', (symbol, interval, limit))
    data = c.fetchall()
    conn.close()
    if not data:
        return pd.DataFrame()
    columns = ['open_time', 'open', 'high', 'low', 'close', 'volume']
    df = pd.DataFrame(data, columns=columns)
    df = df.iloc[::-1].reset_index(drop=True)
    return df

def get_support_resistance(df):
    window = min(20, len(df))
    recent_highs = df['high'].tail(window)
    recent_lows = df['low'].tail(window)
    resistance = recent_highs.max()
    support = recent_lows.min()
    return support, resistance

def format_indicator_box(label, value, color, font_size=20):
    return ar(f"[b][color={color}]{label}[/color][/b]\n[b][color=ffffff]{value}[/color][/b]")

def analyze_crypto(symbol, interval, df):
    if df.empty or len(df) < 21:
        return ar("[color=ea4335][b]لا توجد بيانات كافية للتحليل.[/b][/color]"), "NONE", None, None, None, None, None, {}

    df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
    macd = ta.trend.MACD(df['close'])
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()
    df['sma20'] = ta.trend.SMAIndicator(df['close'], window=20).sma_indicator()
    df['sma50'] = ta.trend.SMAIndicator(df['close'], window=50).sma_indicator()
    df['ema20'] = ta.trend.EMAIndicator(df['close'], window=20).ema_indicator()
    df['ema50'] = ta.trend.EMAIndicator(df['close'], window=50).ema_indicator()
    bb = ta.volatility.BollingerBands(df['close'], window=20)
    df['bb_high'] = bb.bollinger_hband()
    df['bb_low'] = bb.bollinger_lband()
    stoch = ta.momentum.StochasticOscillator(df['high'], df['low'], df['close'])
    df['stoch_k'] = stoch.stoch()
    df['stoch_d'] = stoch.stoch_signal()
    df['cci'] = ta.trend.CCIIndicator(df['high'], df['low'], df['close'], window=20).cci()
    df['adx'] = ta.trend.ADXIndicator(df['high'], df['low'], df['close'], window=14).adx()
    df['williams_r'] = ta.momentum.WilliamsRIndicator(df['high'], df['low'], df['close'], lbp=14).williams_r()
    window = 10
    df['momentum'] = df['close'] - df['close'].shift(window)
    df['obv'] = ta.volume.OnBalanceVolumeIndicator(df['close'], df['volume']).on_balance_volume()
    df['mfi'] = ta.volume.MFIIndicator(df['high'], df['low'], df['close'], df['volume'], window=14).money_flow_index()
    df['atr'] = ta.volatility.AverageTrueRange(df['high'], df['low'], df['close'], window=14).average_true_range()

    signals = []
    entry_price = None
    exit_price = None

    # إشارات التداول (نفس المنطق السابق)
    if df['rsi'].iloc[-1] < 30:
        signals.append(ar('شراء (RSI منخفض)'))
        entry_price = df['close'].iloc[-1]
    elif df['rsi'].iloc[-1] > 70:
        signals.append(ar('بيع (RSI مرتفع)'))
        exit_price = df['close'].iloc[-1]

    if df['macd'].iloc[-1] > df['macd_signal'].iloc[-1] and df['macd'].iloc[-2] <= df['macd_signal'].iloc[-2]:
        signals.append(ar('شراء (تقاطع MACD صاعد)'))
        entry_price = df['close'].iloc[-1]
    elif df['macd'].iloc[-1] < df['macd_signal'].iloc[-1] and df['macd'].iloc[-2] >= df['macd_signal'].iloc[-2]:
        signals.append(ar('بيع (تقاطع MACD هابط)'))
        exit_price = df['close'].iloc[-1]

    if df['sma20'].iloc[-1] > df['sma50'].iloc[-1] and df['sma20'].iloc[-2] <= df['sma50'].iloc[-2]:
        signals.append(ar('شراء (تقاطع SMA صاعد)'))
        entry_price = df['close'].iloc[-1]
    if df['ema20'].iloc[-1] > df['ema50'].iloc[-1] and df['ema20'].iloc[-2] <= df['ema50'].iloc[-2]:
        signals.append(ar('شراء (تقاطع EMA صاعد)'))
        entry_price = df['close'].iloc[-1]
    if df['sma20'].iloc[-1] < df['sma50'].iloc[-1] and df['sma20'].iloc[-2] >= df['sma50'].iloc[-2]:
        signals.append(ar('بيع (تقاطع SMA هابط)'))
        exit_price = df['close'].iloc[-1]
    if df['ema20'].iloc[-1] < df['ema50'].iloc[-1] and df['ema20'].iloc[-2] >= df['ema50'].iloc[-2]:
        signals.append(ar('بيع (تقاطع EMA هابط)'))
        exit_price = df['close'].iloc[-1]

    if df['close'].iloc[-1] < df['bb_low'].iloc[-1]:
        signals.append(ar('شراء (خروج من بولينجر السفلى)'))
        entry_price = df['close'].iloc[-1]
    elif df['close'].iloc[-1] > df['bb_high'].iloc[-1]:
        signals.append(ar('بيع (خروج من بولينجر العليا)'))
        exit_price = df['close'].iloc[-1]

    if df['stoch_k'].iloc[-1] < 20 and df['stoch_d'].iloc[-1] < 20:
        signals.append(ar('شراء (Stochastic منخفض)'))
        entry_price = df['close'].iloc[-1]
    elif df['stoch_k'].iloc[-1] > 80 and df['stoch_d'].iloc[-1] > 80:
        signals.append(ar('بيع (Stochastic مرتفع)'))
        exit_price = df['close'].iloc[-1]

    if df['cci'].iloc[-1] < -100:
        signals.append(ar('شراء (CCI منخفض)'))
        entry_price = df['close'].iloc[-1]
    elif df['cci'].iloc[-1] > 100:
        signals.append(ar('بيع (CCI مرتفع)'))
        exit_price = df['close'].iloc[-1]

    if df['adx'].iloc[-1] > 25:
        signals.append(ar('اتجاه قوي (ADX)'))

    if df['williams_r'].iloc[-1] < -80:
        signals.append(ar('شراء (Williams %R منخفض)'))
        entry_price = df['close'].iloc[-1]
    elif df['williams_r'].iloc[-1] > -20:
        signals.append(ar('بيع (Williams %R مرتفع)'))
        exit_price = df['close'].iloc[-1]

    if df['momentum'].iloc[-1] > 0:
        signals.append(ar('زخم إيجابي'))
    else:
        signals.append(ar('زخم سلبي'))

    if df['mfi'].iloc[-1] < 20:
        signals.append(ar('شراء (MFI منخفض)'))
        entry_price = df['close'].iloc[-1]
    elif df['mfi'].iloc[-1] > 80:
        signals.append(ar('بيع (MFI مرتفع)'))
        exit_price = df['close'].iloc[-1]

    if df['atr'].iloc[-1] > df['atr'].mean():
        signals.append(ar('تقلب عالي (ATR)'))

    buy_count = sum([ar('شراء') in s for s in signals])
    sell_count = sum([ar('بيع') in s for s in signals])
    if buy_count > sell_count and buy_count >= 3:
        main_signal = ar("[color=27ae60][b]توصية: شراء[/b][/color]")
        main_icon = "🟢"
        signal_type = "BUY"
    elif sell_count > buy_count and sell_count >= 3:
        main_signal = ar("[color=ea4335][b]توصية: بيع[/b][/color]")
        main_icon = "🔴"
        signal_type = "SELL"
    else:
        main_signal = ar("[color=fbbc05][b]توصية: انتظار[/b][/color]")
        main_icon = "🟡"
        signal_type = "HOLD"

    support, resistance = get_support_resistance(df)
    last_price = df['close'].iloc[-1]

    indicators_dict = {
        ar("RSI"):      ("%.2f" % df['rsi'].iloc[-1], "e67e22"),
        ar("MACD"):     ("%.4f" % df['macd'].iloc[-1], "9b59b6"),
        ar("MACD Signal"): ("%.4f" % df['macd_signal'].iloc[-1], "9b59b6"),
        ar("SMA20"):    ("%.4f" % df['sma20'].iloc[-1], "3498db"),
        ar("SMA50"):    ("%.4f" % df['sma50'].iloc[-1], "2980b9"),
        ar("EMA20"):    ("%.4f" % df['ema20'].iloc[-1], "16a085"),
        ar("EMA50"):    ("%.4f" % df['ema50'].iloc[-1], "27ae60"),
        ar("بولينجر عالي"): ("%.4f" % df['bb_high'].iloc[-1], "f1c40f"),
        ar("بولينجر منخفض"): ("%.4f" % df['bb_low'].iloc[-1], "f39c12"),
        ar("Stoch K"):  ("%.2f" % df['stoch_k'].iloc[-1], "e84393"),
        ar("Stoch D"):  ("%.2f" % df['stoch_d'].iloc[-1], "6c5ce7"),
        ar("CCI"):      ("%.2f" % df['cci'].iloc[-1], "d35400"),
        ar("ADX"):      ("%.2f" % df['adx'].iloc[-1], "34495e"),
        ar("Williams %R"): ("%.2f" % df['williams_r'].iloc[-1], "fdcb6e"),
        ar("Momentum"): ("%.2f" % df['momentum'].iloc[-1], "636e72"),
        ar("OBV"):      ("%.2f" % df['obv'].iloc[-1], "00b894"),
        ar("MFI"):      ("%.2f" % df['mfi'].iloc[-1], "00cec9"),
        ar("ATR"):      ("%.4f" % df['atr'].iloc[-1], "e17055"),
    }

    entry_text = ar(f"سعر الدخول: [b]{entry_price:.6f}[/b]") if entry_price else ar("سعر الدخول: -")
    exit_text = ar(f"سعر الخروج: [b]{exit_price:.6f}[/b]") if exit_price else ar("سعر الخروج: -")

    summary = (
        ar(f"{main_icon} [b][u]إشارات التداول:[/u][/b]\n")
    )
    for sig in signals:
        summary += f"• {sig}\n"
    summary += f"\n{main_signal}\n"
    summary += ar(f"\nآخر سعر: [b]{last_price:.6f}[/b]\n")
    summary += f"{entry_text}\n{exit_text}\n"
    summary += ar(f"الدعم: [b]{support:.6f}[/b]\nالمقاومة: [b]{resistance:.6f}[/b]\n")
    return summary, signal_type, entry_price, exit_price, support, resistance, last_price, indicators_dict

class ModernCard(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(0.12, 0.14, 0.22, 0.97)
            self.rect = RoundedRectangle(radius=[20], pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class CryptoLiveSimulatorApp(App):
    def build(self):
        create_database()
        self.simulator = TradingSimulator()
        self.main_layout = BoxLayout(orientation='vertical', padding=20, spacing=16)
        self.card = ModernCard(orientation='vertical', padding=18, spacing=14, size_hint=(1, 0.96))

        self.title_label = Label(
            text=ar('[b][color=21aaff]محلل العملات الرقمية[/color][/b]'),
            font_size=34,
            markup=True,
            size_hint=(1, None),
            height=46,
            halign='center',
            valign='middle',
            font_name=ARABIC_FONT_PATH
        )
        self.card.add_widget(self.title_label)

        self.spinner_symbol = Spinner(
            text=CRYPTO_SYMBOLS[0],
            values=CRYPTO_SYMBOLS,
            size_hint=(0.5, None), height=56,
            background_color=(0.21, 0.52, 0.97, 1),
            color=(1,1,1,1),
            font_size=22,
            font_name=ARABIC_FONT_PATH
        )
        self.spinner_interval = Spinner(
            text=ar(INTERVAL_LABELS["1h"]),
            values=[ar(INTERVAL_LABELS[x]) for x in INTERVALS],
            size_hint=(0.5, None), height=56,
            background_color=(0.21, 0.52, 0.97, 1),
            color=(1,1,1,1),
            font_size=22,
            font_name=ARABIC_FONT_PATH
        )

        spinner_box = BoxLayout(orientation='horizontal', size_hint=(1, None), height=66, spacing=16)
        spinner_box.add_widget(Label(text=ar("العملة:"), font_size=22, color=(0.8,0.8,0.8,1), size_hint=(0.25,1), font_name=ARABIC_FONT_PATH))
        spinner_box.add_widget(self.spinner_symbol)
        spinner_box.add_widget(Label(text=ar("الإطار الزمني:"), font_size=22, color=(0.8,0.8,0.8,1), size_hint=(0.25,1), font_name=ARABIC_FONT_PATH))
        spinner_box.add_widget(self.spinner_interval)
        self.card.add_widget(spinner_box)

        self.button = Button(
            text=ar('ابدأ التحليل اللحظي'),
            size_hint=(1, None),
            height=60,
            background_color=(0.21, 0.52, 0.97, 1),
            color=(1, 1, 1, 1),
            font_size=26,
            bold=True,
            background_normal='',
            border=(16,16,16,16),
            font_name=ARABIC_FONT_PATH
        )
        self.button.bind(on_press=self.start_live_analysis)
        self.card.add_widget(self.button)

        self.indicator_grid = GridLayout(cols=3, spacing=8, size_hint_y=None)
        self.indicator_grid.bind(minimum_height=self.indicator_grid.setter('height'))
        self.card.add_widget(self.indicator_grid)

        self.scroll = ScrollView(size_hint=(1, 1))
        self.result_label = Label(
            text=ar("[b]اختر العملة والإطار الزمني ثم اضغط ابدأ التحليل اللحظي.[/b]"),
            font_size=24,
            size_hint_y=None,
            markup=True,
            color=(1,1,1,1),
            halign='right',
            valign='top',
            font_name=ARABIC_FONT_PATH
        )
        self.result_label.bind(texture_size=self.update_height)
        self.scroll.add_widget(self.result_label)
        self.card.add_widget(self.scroll)
        self.main_layout.add_widget(self.card)

        self.is_live = False
        self.sync_thread = None
        self.live_thread = None
        return self.main_layout

    def update_height(self, instance, value):
        self.result_label.height = value[1]
        self.result_label.text_size = (self.result_label.width, None)

    def start_live_analysis(self, instance):
        self.is_live = False
        time.sleep(0.3)
        self.is_live = True
        self.button.text = ar('ايقاف التحليل اللحظي')
        self.simulator = TradingSimulator()
        self.live_thread = threading.Thread(target=self.live_loop, daemon=True)
        self.live_thread.start()
        self.sync_thread = threading.Thread(target=self.sync_history_background, daemon=True)
        self.sync_thread.start()

    def sync_history_background(self):
        symbol = self.spinner_symbol.text
        interval = [k for k,v in INTERVAL_LABELS.items() if ar(v) == self.spinner_interval.text][0]
        try:
            Clock.schedule_once(lambda dt: setattr(self.result_label, 'text', ar("[b]جاري مزامنة البيانات التاريخية... (خلفية)[/b]")))
            sync_full_history(symbol, interval)
            Clock.schedule_once(lambda dt: setattr(self.result_label, 'text', self.result_label.text + ar("\n[color=27ae60]اكتملت مزامنة البيانات.[/color]")))
        except Exception as e:
            Clock.schedule_once(lambda dt: setattr(self.result_label, 'text', self.result_label.text + ar(f"\n[color=ea4335][b]خطأ في مزامنة البيانات:[/b][/color]\n{str(e)}")))

    def update_ui(self, summary, indicators_dict, performance, trades_text, extra):
        self.indicator_grid.clear_widgets()
        for name, (value, color) in indicators_dict.items():
            lbl = Label(
                text=format_indicator_box(name, value, color),
                markup=True,
                font_size=23,
                size_hint_y=None,
                height=80,
                halign='center',
                valign='middle',
                font_name=ARABIC_FONT_PATH
            )
            lbl.text_size = (None, None)
            self.indicator_grid.add_widget(lbl)

        self.result_label.text = (
            summary + extra +
            ar(f"\n\n[محاكاة التداول]\n"
            f"الرصيد: [b]{performance['balance']:.2f} USDT[/b]\n"
            f"الصفقة المفتوحة: [b]{performance['open_position']:.6f}[/b] عند [b]{performance['entry_price'] if performance['entry_price'] else '-'}[/b]\n"
            f"عدد الصفقات: {performance['num_trades']} | ربح: {performance['wins']} | خسارة: {performance['losses']}\n"
            f"إجمالي الربح: [b]{performance['total_profit']:.2f} USDT[/b]\n"
            f"{trades_text}")
        )

    def live_loop(self):
        symbol = self.spinner_symbol.text
        interval = [k for k,v in INTERVAL_LABELS.items() if ar(v) == self.spinner_interval.text][0]
        INTERVAL = 2  # تحديث كل ثانيتين
        while self.is_live:
            start_time = time.time()
            try:
                update_latest_price(symbol, interval)
                df = load_history(symbol, interval, limit=100)
                summary, signal_type, entry_price, exit_price, support, resistance, last_price, indicators_dict = analyze_crypto(symbol, interval, df)

                if signal_type == "BUY" and entry_price and self.simulator.position == 0.0:
                    self.simulator.enter_trade(entry_price)
                if signal_type == "SELL" and exit_price and self.simulator.position > 0.0:
                    self.simulator.exit_trade(exit_price)
                performance = self.simulator.get_performance()
                trades_text = self.simulator.get_trades_log()

                extra = ""
                if signal_type == "BUY" and last_price < support * 1.01:
                    extra += ar("\n[color=27ae60][b]فرصة دخول: السعر قريب من الدعم[/b][/color]")
                elif signal_type == "SELL" and last_price > resistance * 0.99:
                    extra += ar("\n[color=ea4335][b]فرصة خروج: السعر قريب من المقاومة[/b][/color]")

                Clock.schedule_once(lambda dt: self.update_ui(summary, indicators_dict, performance, trades_text, extra))
            except Exception as e:
                err_msg = traceback.format_exc()
                Clock.schedule_once(lambda dt: setattr(self.result_label, 'text', ar(f"[color=ea4335][b]Error during analysis:[/b][/color]\n{err_msg}")))

            elapsed = time.time() - start_time
            sleep_time = max(0, INTERVAL - elapsed)
            time.sleep(sleep_time)

if __name__ == '__main__':
    CryptoLiveSimulatorApp().run()
