import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class RunbookEmailSender:
    def __init__(self):
        self.email_host = os.getenv('EMAIL_HOST')
        self.email_port = int(os.getenv('EMAIL_PORT', 587))
        self.email_user = os.getenv('EMAIL_USER')
        self.email_pass = os.getenv('EMAIL_PASS')
        self.email_recipient = os.getenv('EMAIL_RECIPIENT')
        self.enable_runbook_email = os.getenv('ENABLE_RUNBOOK_EMAIL', 'False').lower() == 'true'
        self.log_file = 'logs/email_log.csv'
        self.ensure_log_file_exists()

    def ensure_log_file_exists(self):
        if not os.path.exists('logs'):
            os.makedirs('logs')
        if not os.path.exists(self.log_file):
            df = pd.DataFrame(columns=['timestamp', 'recipient', 'subject', 'status', 'error'])
            df.to_csv(self.log_file, index=False)

    def log_email_activity(self, recipient, subject, status, error=None):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        new_log = pd.DataFrame([{'timestamp': timestamp, 'recipient': recipient, 'subject': subject, 'status': status, 'error': error}])
        new_log.to_csv(self.log_file, mode='a', header=False, index=False)

    def convert_html_to_pdf(self, html_path, pdf_path):
        # This is a placeholder. Real implementation would use a library like WeasyPrint or wkhtmltopdf
        # For example, using WeasyPrint:
        # from weasyprint import HTML
        # HTML(html_path).write_pdf(pdf_path)
        print(f"Converting {html_path} to {pdf_path} (placeholder - actual conversion not implemented)")
        # Dummy PDF creation for demonstration
        with open(pdf_path, 'w') as f:
            f.write("Dummy PDF content for runbook")
        return os.path.exists(pdf_path)

    def send_runbook_email(self, runbook_html_path):
        if not self.enable_runbook_email:
            print("Runbook email sending is disabled by ENABLE_RUNBOOK_EMAIL flag.")
            self.log_email_activity(self.email_recipient, "Runbook Email (Disabled)", "Skipped", "Email sending disabled")
            return False

        if not all([self.email_host, self.email_port, self.email_user, self.email_pass, self.email_recipient]):
            print("Email configuration missing in .env. Cannot send runbook email.")
            self.log_email_activity(self.email_recipient, "Runbook Email", "Failed", "Missing configuration")
            return False

        pdf_path = runbook_html_path.replace('.html', '.pdf')
        if not self.convert_html_to_pdf(runbook_html_path, pdf_path):
            self.log_email_activity(self.email_recipient, "Runbook Email", "Failed", "PDF conversion failed")
            return False

        msg = MIMEMultipart()
        msg['From'] = self.email_user
        msg['To'] = self.email_recipient
        msg['Subject'] = f"Daily Runbook - {datetime.now().strftime('%Y-%m-%d')}"

        body = "Please find attached today's runbook."
        msg.attach(MIMEText(body, 'plain'))

        try:
            with open(pdf_path, 'rb') as f:
                attach = MIMEApplication(f.read(), _subtype="pdf")
                attach.add_header('Content-Disposition', 'attachment', filename=os.path.basename(pdf_path))
                msg.attach(attach)
        except Exception as e:
            print(f"Error attaching PDF: {e}")
            self.log_email_activity(self.email_recipient, msg['Subject'], "Failed", f"Attachment error: {e}")
            return False

        try:
            with smtplib.SMTP(self.email_host, self.email_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_pass)
                server.send_message(msg)
            print(f"Runbook email sent successfully to {self.email_recipient}")
            self.log_email_activity(self.email_recipient, msg['Subject'], "Success")
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            self.log_email_activity(self.email_recipient, msg['Subject'], "Failed", str(e))
            return False

if __name__ == '__main__':
    # Example Usage:
    # Create a dummy HTML file for testing
    dummy_html_path = 'dummy_runbook.html'
    with open(dummy_html_path, 'w') as f:
        f.write("<html><body><h1>Dummy Runbook</h1><p>This is a test runbook.</p></body></html>")

    sender = RunbookEmailSender()
    sender.send_runbook_email(dummy_html_path)

    # Clean up dummy file
    if os.path.exists(dummy_html_path):
        os.remove(dummy_html_path)
    dummy_pdf_path = dummy_html_path.replace('.html', '.pdf')
    if os.path.exists(dummy_pdf_path):
        os.remove(dummy_pdf_path)