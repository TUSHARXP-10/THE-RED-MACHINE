import requests
import os
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class TelegramSignalBot:
    def __init__(self):
        self.telegram_token = os.getenv('TELEGRAM_TOKEN')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.enable_signal_alerts = os.getenv('ENABLE_SIGNAL_ALERTS', 'False').lower() == 'true'
        self.log_file = 'logs/telegram_log.csv'
        self.ensure_log_file_exists()

    def ensure_log_file_exists(self):
        if not os.path.exists('logs'):
            os.makedirs('logs')
        if not os.path.exists(self.log_file):
            df = pd.DataFrame(columns=['timestamp', 'message', 'status', 'error'])
            df.to_csv(self.log_file, index=False)

    def log_telegram_activity(self, message, status, error=None):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        new_log = pd.DataFrame([{'timestamp': timestamp, 'message': message, 'status': status, 'error': error}])
        new_log.to_csv(self.log_file, mode='a', header=False, index=False)

    def send_signal_alert(self, strategy_name, action, price, symbol, timestamp=None):
        if not self.enable_signal_alerts:
            print("Telegram signal alerts are disabled by ENABLE_SIGNAL_ALERTS flag.")
            self.log_telegram_activity("Signal Alert (Disabled)", "Skipped", "Alerts disabled")
            return False

        if not all([self.telegram_token, self.telegram_chat_id]):
            print("Telegram configuration missing in .env. Cannot send signal alert.")
            self.log_telegram_activity("Signal Alert", "Failed", "Missing configuration")
            return False

        if timestamp is None:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        message = (
            f"🚨 *New Trading Signal* 🚨\n"
            f"*Strategy*: {strategy_name}\n"
            f"*Action*: {action}\n"
            f"*Symbol*: {symbol}\n"
            f"*Price*: {price}\n"
            f"*Time*: {timestamp}"
        )

        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        params = {
            'chat_id': self.telegram_chat_id,
            'text': message,
            'parse_mode': 'Markdown'
        }

        try:
            response = requests.post(url, params=params)
            response.raise_for_status()
            print(f"Telegram alert sent successfully to chat {self.telegram_chat_id}")
            self.log_telegram_activity(message, "Success")
            return True
        except Exception as e:
            print(f"Failed to send Telegram alert: {e}")
            self.log_telegram_activity(message, "Failed", str(e))
            return False

if __name__ == '__main__':
    # Example Usage:
    bot = TelegramSignalBot()
    bot.send_signal_alert(
        strategy_name="DummySENSEXStrategy",
        action="BUY",
        price=75000,
        symbol="SENSEX",
        timestamp="2023-11-15 10:30:00"
    )