import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

load_dotenv()

EMAIL_SENDER = os.getenv("EMAIL_SENDER", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER", "")

def test_email():
    try:
        msg = MIMEMultipart()
        msg["Subject"] = "🧪 Test Email from Job Agent"
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_RECEIVER

        body = """
        <html>
        <body>
            <h2>✅ Email Test Successful!</h2>
            <p>Your Job Agent email configuration is working.</p>
        </body>
        </html>
        """
        msg.attach(MIMEText(body, "html"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        server.quit()

        print("✅ Email sent successfully!")
        print(f"   From: {EMAIL_SENDER}")
        print(f"   To: {EMAIL_RECEIVER}")

    except Exception as e:
        print(f"❌ Email failed: {e}")

if __name__ == "__main__":
    test_email()