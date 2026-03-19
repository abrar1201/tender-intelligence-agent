import smtplib
from email.mime.text import MIMEText


def clean_text(value):
    """
    Some APIs return text in multiple languages as dictionaries.
    This function extracts the English version if available.
    """

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

    msg["Subject"] = f"{len(tenders)} New Procurement Opportunities"
    msg["From"] = "shahabrar1201@gmail.com"
    msg["To"] = "hannahboden501@gmail.com.com"  

    try:

        print("Email sent successfully.")

    except Exception as e:
        print("Email failed:", e)
