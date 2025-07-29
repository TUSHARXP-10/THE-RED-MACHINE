import smtplib
from email.mime.text import MIMEText
def send_alert(subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = "your@email.com"
    msg["To"] = "yourself@email.com"

    with smtplib.SMTP("smtp.gmail.com", 587) as s:
        s.starttls()
        s.login("your@email.com", "your_password")
        s.sendmail(msg["From"], [msg["To"]], msg.as_string())