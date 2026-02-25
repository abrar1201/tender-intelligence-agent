import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SENDER_EMAIL = os.environ.get("EMAIL_USER")
SENDER_PASSWORD = os.environ.get("EMAIL_PASS")

RECIPIENTS = [
    "arjun.kondisetti@purplemavens.com",
    "hannahboden501@gmail.com",
    "srikanth@purplemavens.com"
]


def send_email(tenders):

    if not SENDER_EMAIL or not SENDER_PASSWORD:
        print("Email credentials not set.")
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Tender Intelligence Report"
    msg["From"] = SENDER_EMAIL
    msg["To"] = ", ".join(RECIPIENTS)

    html = "<h2>ERP-Relevant Tenders</h2><ul>"

    for t in tenders:
        html += f"""
        <li>
            <b>{t['title']}</b><br>
            Score: {round(t['similarity'], 3)}<br>
            Source: {t.get('source', 'N/A')}<br>
            <a href="{t['link']}">{t['link']}</a>
        </li><br>
        """

    html += "</ul>"

    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECIPIENTS, msg.as_string())

        print("✅ Email sent successfully.")

    except Exception as e:
        print("❌ Email failed:", e)