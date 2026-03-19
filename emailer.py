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

    html = f"""
<html>
<body style="font-family: Arial, sans-serif; background-color:#f4f6f8; padding:20px;">

    <div style="max-width:600px; margin:auto; background:white; padding:20px; border-radius:10px;">

        <h2 style="color:#2c3e50;">🚀 Procurement Intelligence Report</h2>

        <p style="color:#555;">
            📊 <b>{len(tenders)} New Opportunities Found</b><br>
            🕒 Generated Automatically
        </p>

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
            <div style="
                background:#ffffff;
                border:1px solid #e0e0e0;
                padding:15px;
                margin-bottom:15px;
                border-radius:8px;
            ">

                <h3 style="margin:0; color:#34495e;">💼 {title}</h3>

                <p style="margin:8px 0; color:#555;">
                    🏢 <b>{org}</b><br>
                    📅 Deadline: {deadline}
                </p>

                <a href="{link}" 
                    style="
                    display:inline-block;
                    padding:10px 15px;
                    background:#007bff;
                    color:white;
                    text-decoration:none;
                    border-radius:5px;
                    font-size:14px;
                ">
               🔗 View Tender
            </a>

        </div>
    """
    html += """
        <hr>

        <p style="font-size:12px; color:#888;">
            This is an automated procurement intelligence alert.
        </p>

    </div>
</body>
</html>
"""

    msg = MIMEText(html, "html")

    sender = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")

    receivers = [
    "hannahboden501@gmail.com",
    "arjun.kondisetti@purplemavens.com",
    "srikanth@purplemavens.com",
    "sannadate@gmail.com"
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
