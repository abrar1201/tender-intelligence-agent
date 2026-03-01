from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")

MAZE_PROFILE = """
Enterprise Resource Planning (ERP) systems.
SAP implementation or migration.
Oracle ERP Cloud.
Microsoft Dynamics 365.
Enterprise Asset Management (EAM).
Supply Chain Management (SCM).
Human Capital Management (HCM).
Customer Relationship Management (CRM).
Digital transformation programmes.
Legacy system replacement.
Enterprise IT modernization.
System integrator services.
Government ERP upgrade.
Core business systems implementation.
"""


profile_embedding = model.encode(MAZE_PROFILE, convert_to_tensor=True)

KEYWORDS = [
    "ERP",
    "SAP",
    "Oracle",
    "Microsoft Dynamics 365",
    "MS Dynamics 365",
    "Dynamics 365",
    "D365",
    "Dynamics CRM",
    "CRM",
    "HCM",
    "SCM",
    "EAM",
    "enterprise system",
    "digital transformation",
    "system integrator",
    "core system",
    "business systems"
]

def keyword_boost(text):
    text_lower = text.lower()
    score = 0
    for kw in KEYWORDS:
        if kw.lower() in text_lower:
            if "dynamics" in kw.lower():
                score += 0.1
            else:
                score += 0.05
    return score

def calculate_similarity(text):
    tender_embedding = model.encode(text, convert_to_tensor=True)
    score = float(util.cos_sim(profile_embedding, tender_embedding))
    score += keyword_boost(text)
    return score
