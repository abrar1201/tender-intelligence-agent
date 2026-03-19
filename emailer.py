import smtplib
import os
from email.mime.text import MIMEText


def clean_text(value):
    if isinstance(value, dict):
        return value.get("en") or list(value.values())[0]
    return value


def send_email(tenders):

    if not tenders:
        print("No relevant tenders to email.")
        return

    html = """
    <h2>New Procurement Opportunities</h2>
    <hr>
    """

    for t in tenders:

        title = clean_text(t.get("title", "No title"))
        org = clean_text(t.get("organization", "Unknown organization"))
        deadline = clean_text(t.get("deadline", "Not specified"))
        link = t.get("url") or t.get("link", "#")

        if link and not link.startswith("http"):
            link = "https://" + link

        html += f"""
        <p>
        <b>{title}</b><br>
        Organization: {org}<br>
        Deadline: {deadline}<br>
        <a href="{link}">🔗 View Tender</a>
        </p>
        <hr>
        """

    msg = MIMEText(html, "html")

    sender = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")

    receivers = [
    "hannahboden501@gmail.com",
]

    msg["Subject"] = f"{len(tenders)} New Procurement Opportunities"
    msg["From"] = sender
    msg["To"] = ", ".join(receivers)

    try:
        print("Connecting to Gmail SMTP...")

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()

        print("Logging in...")
        server.login(sender, password)

        print("Sending email...")
        server.sendmail(sender, receivers, msg.as_string())

        server.quit()

        print("✅ Email SENT successfully")

    except Exception as e:
        print("❌ Email FAILED:", e)