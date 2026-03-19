import requests
import os

DYNAMICS_URL = os.getenv("DYNAMICS_URL")
DYNAMICS_TOKEN = os.getenv("DYNAMICS_TOKEN")

def create_lead(tender):

    if not DYNAMICS_URL or not DYNAMICS_TOKEN:
        print("Dynamics not configured.")
        return

    headers = {
        "Authorization": f"Bearer {DYNAMICS_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "subject": tender["title"],
        "description": tender["description"][:2000],
        "new_country": tender.get("country", "Unknown"),
        "new_score": tender.get("score", 0)
    }

    response = requests.post(
        f"{DYNAMICS_URL}/api/data/v9.2/leads",
        headers=headers,
        json=payload
    )

    print("Dynamics response:", response.status_code)