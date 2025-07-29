import os
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class DailyDigest:
    def __init__(self):
        self.sender_email = os.getenv("SENDER_EMAIL")
        self.sender_password = os.getenv("SENDER_PASSWORD")
        self.recipient_email = os.getenv("RECIPIENT_EMAIL")
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))

    def get_summary_data(self):
        # Load backtest results
        try:
            backtest_results = pd.read_csv('backtest_results.csv')
            if not backtest_results.empty:
                # Assuming the last run's results are most relevant or aggregate as needed
                total_trades = backtest_results['Total Trades'].sum()
                total_pnl = backtest_results['Avg PnL'].sum() * backtest_results['Total Trades'].sum() # Simplified
                strategies_fired = ", ".join(backtest_results['Strategy Name'].tolist())
                accuracy = backtest_results['Accuracy'].mean()
                
                # Placeholder for actual model accuracy if available elsewhere
                model_accuracy = f"{accuracy*100:.1f}%"

                return {
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "model_accuracy": model_accuracy,
                    "strategies_fired": strategies_fired,
                    "trades_executed": total_trades,
                    "net_pnl": f"₹ {total_pnl:,.0f}"
                }
            else:
                return None
        except FileNotFoundError:
            print("backtest_results.csv not found. Please run strategy_lab.py first.")
            return None
        except Exception as e:
            print(f"Error loading backtest results: {e}")
            return None

    def create_email_body(self, summary_data):
        if not summary_data:
            return "No data available for daily digest."

        html_body = f"""
        <html>
            <body>
                <h1 style="color: #4CAF50;">📈 RED MACHINE DAILY DIGEST 📈</h1>
                <p>📅 <b>Date:</b> {summary_data['date']}</p>
                <p>📊 <b>Model Accuracy:</b> {summary_data['model_accuracy']}</p>
                <p>🧠 <b>Strategies Fired:</b> {summary_data['strategies_fired']}</p>
                <p>🧾 <b>Trades Executed:</b> {summary_data['trades_executed']}</p>
                <p>💰 <b>Net P&L:</b> {summary_data['net_pnl']}</p>
                <br>
                <p>📎 See attached charts for more.</p>
                <p>🔍 Strategy Overview Attached.</p>
            </body>
        </html>
        """
        return html_body

    def send_email(self, subject, body, attachments=None):
        if not self.sender_email or not self.sender_password or not self.recipient_email:
            print("Email credentials not set in .env file. Skipping email.")
            return

        msg = MIMEMultipart('alternative')
        msg['From'] = self.sender_email
        msg['To'] = self.recipient_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'html'))

        if attachments:
            for attachment_path in attachments:
                try:
                    with open(attachment_path, 'rb') as f:
                        img = MIMEImage(f.read())
                        img.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attachment_path))
                        msg.attach(img)
                except FileNotFoundError:
                    print(f"Attachment not found: {attachment_path}")
                except Exception as e:
                    print(f"Error attaching file {attachment_path}: {e}")

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # Secure the connection
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            print("Daily digest email sent successfully!")
        except Exception as e:
            print(f"Failed to send email: {e}")

    def run_digest(self):
        summary_data = self.get_summary_data()
        email_body = self.create_email_body(summary_data)
        
        attachments = []
        results_dir = 'results'
        if os.path.exists(results_dir):
            for f in os.listdir(results_dir):
                if f.endswith(('.png', '.jpg', '.jpeg')):
                    attachments.append(os.path.join(results_dir, f))

        self.send_email("Red Machine Daily Digest", email_body, attachments)

if __name__ == "__main__":
    digest = DailyDigest()
    digest.run_digest()