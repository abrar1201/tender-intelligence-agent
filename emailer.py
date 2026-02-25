import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import sqlite3

SENDER_EMAIL = "shahabrar1201@gmail.com"
SENDER_PASSWORD = "lvxwlzmvetwcqowu"

RECIPIENTS = [
    "arjun.kondisetti@purplemavens.com",
    "hannahboden501@gmail.com",
    "srikanth@purplemavens.com"
]

def send_daily_summary():
    conn = sqlite3.connect("tenders.db")
    c = conn.cursor()

    c.execute("""
    SELECT title, similarity, link, source
    FROM tenders
    WHERE created_at >= datetime('now', '-1 day')
    ORDER BY similarity DESC
""")
    rows = c.fetchall()
    conn.close()

    if not rows:
        print("No new tenders to email.")
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Daily Tender Intelligence Report"
    msg["From"] = SENDER_EMAIL
    msg["To"] = ", ".join(RECIPIENTS)

    html = "<h2>Daily ERP-Relevant Tenders</h2><ul>"

    for r in rows:
        html += f"""
        <li>
            <b>{r[0]}</b><br>
            Score: {round(r[1], 3)}<br>
            Source: {r[3]}<br>
            <a href="{r[2]}">{r[2]}</a>
        </li><br>
        """

    html += "</ul>"

    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENTS, msg.as_string())

    print("Daily email sent successfully.")