KEYWORDS = [
    # Core ERP/CRM/system keywords
    "erp",
    "crm",
    "hcm",
    "scm",
    "eam",
    "enterprise resource planning",
    "customer relationship management",
    "human capital management",
    "supply chain management",
    "asset management system",

    # Transformation & IT
    "digital transformation",
    "enterprise system",
    "it solution",
    "it services",
    "software development",
    "system integration",
    "managed service",
    "cloud service",
    "technology solution",
    "it infrastructure",
    "it support",
    "it procurement",
    "ict",
    "information technology",
    "information system",
    "business system",
    "business intelligence",
    "data analytics",
    "cybersecurity",
    "cyber security",

    # Specific platforms
    "sap",
    "oracle",
    "dynamics 365",
    "microsoft dynamics",
    "netsuite",
    "salesforce",
    "workday",
    "sage",
    "infor",
    "unit4",
    "epicor",

    # Procurement/tender types
    "implementation",
    "software procurement",
    "system procurement",
    "rfp",
    "rft",
    "framework agreement",
    "managed it",
    "digital services",

    # UK/FTS specific common terms
    "software",
    "platform",
    "application",
    "solution",
    "system",
    "database",
    "network",
    "infrastructure",
    "licence",
    "licensing",
    "support contract",
    "maintenance contract",
    "service desk",
    "helpdesk",
    "project management",
    "consultancy",
    "technology",
]


def is_relevant(t):
    text = (
        (t.get("title") or "") + " " + (t.get("description") or "")
    ).lower()

    keyword_match = any(k in text for k in KEYWORDS)
    similarity = t.get("similarity", None)
    source = t.get("source", "")

    # ✅ UK and FTS — bypass similarity, use keywords only
    # These sources have short titles that score low on semantic similarity
    # but are perfectly valid procurement tenders
    if source in ("uk", "findatender"):
        if keyword_match:
            print(f"  [PASSED - keyword] source={source} | title={t.get('title', '')[:60]}")
        else:
            print(f"  [DROPPED - no keyword] source={source} | title={t.get('title', '')[:60]}")
        return keyword_match

    # For sources with no similarity score, keyword match is enough
    if similarity is None:
        return keyword_match

    # For AI-scored sources, require keyword + low similarity OR high similarity alone
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