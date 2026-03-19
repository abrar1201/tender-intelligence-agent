KEYWORDS = ["erp", "crm", "hcm", "scm", "eam",
    "enterprise resource planning",
    "customer relationship management",
    "human capital management",
    "supply chain management",
    "asset management system",
    "digital transformation",
    "enterprise system",
    "sap", "oracle", "dynamics 365",
    "netsuite", "salesforce",
    "implementation", "system integration",
    "it solution", "software development"]

# portal_classifier.py

def is_relevant(t):
    text = ((t.get("title") or "") + " " + (t.get("description") or "")).lower()
    keyword_match = any(k in text for k in KEYWORDS)
    similarity = t.get("similarity", None)

    # ✅ UK and FTS — keyword only, don't penalise with similarity threshold
    if t.get("source") in ("uk", "findatender"):
        return keyword_match

    if similarity is None:
        return keyword_match

    if keyword_match and similarity > 0.10:
        return True

    if similarity > 0.25:
        return True

    return False


def is_procurement_portal(text):

    text = text.lower()

    for k in KEYWORDS:

        if k in text:

            return True

    return False