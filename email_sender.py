# email_sender.py
# email_sender.py — secure env var usage
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Read environment variables (set these in PythonAnywhere )
SENDER_EMAIL = os.environ.get("mrudhumrudalinibr@gmail.com")       # e.g. mrudhumrudalinibr@gmail.com
APP_PASSWORD = os.environ.get("kybr crcz ezsk lqiw")       # app-specific password or SMTP password

SEND_EMAILS = os.environ.get("CV_SEND_EMAILS", "0") == "1"

def send_allotment_email(to_email, student_name, branch):
    if not to_email or "@" not in to_email:
        print(f"Invalid email, skipping: {to_email}")
        return False

    subject = "Your Seat Allotment Result – CodeVision AI Engineering College"
    body = f"""Dear {student_name},

Congratulations!

Your seat has been successfully allotted.

Allocated Branch: {branch} Engineering

Please log in to the portal to view complete details.

Regards,
CodeVision AI Engineering College
Admissions Department
"""

    # Do NOT send real email unless CV_SEND_EMAILS=1
    if not SEND_EMAILS:
        print(f"[TEST MODE] Email to {to_email}:\n{body}")
        return True

    if not SENDER_EMAIL or not APP_PASSWORD:
        print("Email credentials not set. Cannot send email.")
        return False

    try:
        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.send_message(msg)
        server.quit()

        print(f"Email sent to {to_email}")
        return True

    except Exception as e:
        print(f"Email sending failed: {e}")
        return False
