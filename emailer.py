import os
import smtplib
from email.mime.text import MIMEText
from html import escape


def clean_text(value):
    if isinstance(value, dict):
        return value.get("en") or value.get("ENG") or next(iter(value.values()), "")
    if value is None:
        return ""
    if isinstance(value, list):
        return ", ".join(str(v) for v in value if v)
    return str(value)


def get_link(tender):
    link = clean_text(tender.get("url") or tender.get("link")).strip()
    if link and not link.startswith(("http://", "https://")):
        link = "https://" + link
    return link


def infer_sector(tender):
    source = clean_text(tender.get("source")).lower()
    text = f"{tender.get('title', '')} {tender.get('description', '')}".lower()

    if "water" in text:
        return "Water"
    if source in ("uk", "findatender"):
        return "Public Sector"
    if source == "ted":
        return "EU Public Sector"
    if source in ("samgov", "sam.gov"):
        return "US Federal"
    if source in ("worldbank", "adb"):
        return "Development Bank"
    return "General"


def infer_opportunity_area(tender):
    categories = tender.get("category") or []
    if categories:
        labels = {
            "erp": "ERP",
            "crm": "CRM",
            "hcm": "HCM / HR",
            "scm": "SCM",
            "eam": "EAM / Asset Management",
        }
        return ", ".join(labels.get(str(c).lower(), str(c).upper()) for c in categories)
    return clean_text(tender.get("title")) or "Tender Opportunity"


def infer_status(tender):
    deadline = clean_text(tender.get("deadline")).strip()
    if deadline:
        return f"Open - deadline {deadline}"
    return "New Opportunity"


def infer_route(tender):
    source = clean_text(tender.get("source")).strip()
    route_by_source = {
        "uk": "Contracts Finder",
        "findatender": "Find a Tender",
        "ted": "TED Portal",
        "samgov": "SAM.gov",
        "SAM.gov": "SAM.gov",
        "worldbank": "World Bank",
        "adb": "ADB",
        "austender": "AusTender",
        "Canada": "Canada Tender Portal",
        "globaltenders": "Global Tenders",
    }
    return route_by_source.get(source, source or "Supplier Portal")


def infer_priority(tender):
    score = tender.get("similarity")
    if score is None:
        return "High"
    if score >= 0.45:
        return "Very High"
    if score >= 0.35:
        return "High"
    return "Medium"


def build_table_rows(tenders):
    rows = []

    for tender in tenders:
        title = clean_text(tender.get("title")).strip() or "View tender"
        organisation = (
            clean_text(tender.get("organization")).strip()
            or clean_text(tender.get("authority")).strip()
            or clean_text(tender.get("source")).strip()
            or "Unknown organisation"
        )
        sector = infer_sector(tender)
        opportunity_area = infer_opportunity_area(tender)
        tender_value = clean_text(tender.get("value") or tender.get("tender_value")).strip() or "TBC"
        status = infer_status(tender)
        route = infer_route(tender)
        priority = infer_priority(tender)
        link = get_link(tender)

        if link:
            source_evidence = (
                f'<a href="{escape(link)}" '
                'style="color:#8ea0ff; text-decoration:underline;">'
                f"{escape(title)}</a>"
            )
        else:
            source_evidence = escape(title)

        rows.append(f"""
            <tr>
                <td style="border:1px solid #555; padding:10px 8px; vertical-align:middle;">{escape(organisation)}</td>
                <td style="border:1px solid #555; padding:10px 8px; vertical-align:middle;">{escape(sector)}</td>
                <td style="border:1px solid #555; padding:10px 8px; vertical-align:middle;">{escape(opportunity_area)}</td>
                <td style="border:1px solid #555; padding:10px 8px; vertical-align:middle;">{escape(tender_value)}</td>
                <td style="border:1px solid #555; padding:10px 8px; vertical-align:middle;">{escape(status)}</td>
                <td style="border:1px solid #555; padding:10px 8px; vertical-align:middle;">{escape(route)}</td>
                <td style="border:1px solid #555; padding:10px 8px; vertical-align:middle;">{source_evidence}</td>
                <td style="border:1px solid #555; padding:10px 8px; vertical-align:middle;">{escape(priority)}</td>
            </tr>
        """)

    return "\n".join(rows)


def build_email_html(tenders):
    table_rows = build_table_rows(tenders)

    return f"""
<html>
<body style="font-family: Arial, sans-serif; background-color:#1f1f1f; padding:20px; margin:0;">
    <div style="max-width:1200px; margin:auto; background:#262626; padding:20px; border-radius:6px;">
        <h2 style="color:#f2f2f2; margin:0 0 8px;">Procurement Intelligence Report</h2>

        <p style="color:#d8d8d8; margin:0 0 18px;">
            <b>{len(tenders)} New Opportunities Found</b><br>
            Generated automatically
        </p>

        <table role="presentation" cellspacing="0" cellpadding="0" style="width:100%; border-collapse:collapse; table-layout:fixed; color:#f2f2f2; font-size:14px; line-height:1.35;">
            <thead>
                <tr>
                    <th style="border:1px solid #666; padding:10px 8px; text-align:left; width:15%;">Organisation</th>
                    <th style="border:1px solid #666; padding:10px 8px; text-align:left; width:10%;">Sector</th>
                    <th style="border:1px solid #666; padding:10px 8px; text-align:left; width:17%;">Opportunity Area</th>
                    <th style="border:1px solid #666; padding:10px 8px; text-align:left; width:10%;">Potential Tender Value</th>
                    <th style="border:1px solid #666; padding:10px 8px; text-align:left; width:14%;">Current Status</th>
                    <th style="border:1px solid #666; padding:10px 8px; text-align:left; width:14%;">Likely Procurement Route</th>
                    <th style="border:1px solid #666; padding:10px 8px; text-align:left; width:14%;">Source / Evidence</th>
                    <th style="border:1px solid #666; padding:10px 8px; text-align:left; width:8%;">Priority</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>

        <p style="font-size:12px; color:#bdbdbd; margin:18px 0 0;">
            This is an automated procurement intelligence alert.
        </p>
    </div>
</body>
</html>
"""


def send_email(tenders):
    if not tenders:
        print("No relevant tenders to email.")
        return

    msg = MIMEText(build_email_html(tenders), "html")

    sender = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")

    receivers = [
    "hannahboden501@gmail.com",
    "arjun.kondisetti@purplemavens.com",
    "srikanth@purplemavens.com",
    # "sannadate@gmail.com"
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

        print("Email SENT successfully")

    except Exception as e:
        print("Email FAILED:", e)
