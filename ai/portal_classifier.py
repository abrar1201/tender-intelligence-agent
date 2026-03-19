KEYWORDS = ["ERP", "SAP", "Oracle", "Dynamics", "CRM"]

def is_relevant(t):
    text = (t.get("title") or "") + " " + (t.get("description") or "")

    keyword_match = any(k.lower() in text.lower() for k in KEYWORDS)
    similarity_match = t.get("similarity", 0) > 0.15

    return keyword_match or similarity_match


def is_procurement_portal(text):

    text = text.lower()

    for k in KEYWORDS:

        if k in text:

            return True

    return False