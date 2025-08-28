# test_email_notification.py - Simple script to test email notifications

import os
import logging
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Load environment variables
load_dotenv()
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT")

def test_email_notification():
    """Test sending email notifications"""
    logging.info("Testing email notification system...")
    
    # Check if environment variables are set
    if not all([EMAIL_HOST, EMAIL_PORT, EMAIL_USER, EMAIL_PASS, EMAIL_RECIPIENT]):
        logging.error("Missing required environment variables for email. Please check your .env file.")
        logging.info("Required variables: EMAIL_HOST, EMAIL_PORT, EMAIL_USER, EMAIL_PASS, EMAIL_RECIPIENT")
        return False
    
    logging.info("Email configuration loaded successfully")
    logging.info(f"Email Host: {EMAIL_HOST}")
    logging.info(f"Email Port: {EMAIL_PORT}")
    logging.info(f"Email User: {EMAIL_USER}")
    logging.info(f"Email Recipient: {EMAIL_RECIPIENT}")
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = EMAIL_RECIPIENT
        msg['Subject'] = f"Trading System Test Email - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        body = f"""
        <html>
        <body>
            <h2>Trading System Test Email</h2>
            <p>This is a test email from your trading system to verify that email notifications are working correctly.</p>
            <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <hr>
            <p><em>If you received this email, your email notification system is configured correctly!</em></p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        # Connect to server and send email
        logging.info(f"Connecting to email server {EMAIL_HOST}:{EMAIL_PORT}...")
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        
        logging.info("Logging in to email server...")
        server.login(EMAIL_USER, EMAIL_PASS)
        
        logging.info("Sending test email...")
        server.send_message(msg)
        server.quit()
        
        logging.info(f"Test email sent successfully to {EMAIL_RECIPIENT}")
        return True
    except Exception as e:
        logging.error(f"Failed to send test email: {e}")
        return False

if __name__ == "__main__":
    print("\n===== Email Notification Test =====\n")
    result = test_email_notification()
    print("\n===== Test Results =====")
    if result:
        print("✅ Email notification test successful!")
        print(f"A test email has been sent to {EMAIL_RECIPIENT}.")
        print("Please check your inbox to confirm receipt.")
    else:
        print("❌ Email notification test failed!")
        print("Please check the logs above for details on what went wrong.")
    print("\n=================================")