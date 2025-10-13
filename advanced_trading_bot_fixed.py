import logging
import time
import signal
import traceback

# إعداد تسجيل الأحداث
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TradingBot:
    def __init__(self, paper_trading=True):
        self.paper_trading = paper_trading
        self.open_orders = []
        self.position = None

    def cancel_all_orders(self):
        """إلغاء جميع الأوامر المعلقة"""
        logging.info("إلغاء جميع الأوامر المعلقة.")
        self.open_orders.clear()

    def get_all_open_orders(self):
        """الحصول على جميع الأوامر المفتوحة"""
        logging.info("الحصول على جميع الأوامر المفتوحة.")
        return self.open_orders

    def manage_risk_fixed(self):
        """إدارة المخاطر - إلغاء الأوامر المتبقية بعد إغلاق المركز"""
        if self.position is None:
            self.cancel_all_orders()

    def trading_loop_fixed(self):
        """الحلقة الرئيسية للتداول مع تنظيف الأوامر"""
        try:
            while True:
                # هنا يتم تنفيذ استراتيجيات التداول
                logging.info("تنفيذ استراتيجيات التداول.")
                time.sleep(5)  # محاكاة وقت الانتظار بين كل عملية تداول
        except Exception as e:
            logging.error(f"حدث خطأ: {e}")
            logging.debug(traceback.format_exc())
        finally:
            self.cancel_all_orders()
            logging.info("تم تنظيف الأوامر عند إنهاء البرنامج.")

    def signal_handler(self, sig, frame):
        """معالج الإشارة لإغلاق آمن"""
        logging.info("تم تلقي إشارة إنهاء، سيتم إنهاء البرنامج.")
        self.cancel_all_orders()
        exit(0)

if __name__ == "__main__":
    trading_bot = TradingBot(paper_trading=True)
    signal.signal(signal.SIGINT, trading_bot.signal_handler)  # التعامل مع Ctrl+C
    trading_bot.trading_loop_fixed()