from sentence_transformers import SentenceTransformer, util
import torch

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# ─────────────────────────────────────────────────────────────────────────────
# REFERENCE SENTENCES
# These must be specific enough that only real enterprise software tenders
# match. Avoid generic words like "procurement" or "management" alone —
# they match World Bank procurement reform reports, construction management,
# and other non-IT content.
# ─────────────────────────────────────────────────────────────────────────────
REFERENCE_SENTENCES = [
    # ERP — specific enough to not match generic procurement
    "ERP software implementation and deployment tender",
    "Enterprise resource planning system procurement and rollout",
    "SAP ERP implementation services request for proposal",
    "Oracle Dynamics 365 NetSuite enterprise software tender",
    "ERP system integration and go-live support services",

    # CRM
    "Customer relationship management CRM software implementation",
    "Salesforce Microsoft Dynamics CRM platform deployment tender",
    "CRM system procurement and integration services",

    # HR / HCM / Payroll — very specific to software, not HR services
    "HR human resources management software system implementation",
    "Payroll software system procurement and deployment",
    "HRIS HRMS human capital management platform tender",
    "Workforce management software implementation services",
    "Employee management system software procurement tender",
    "Staff scheduling and workforce planning software deployment",

    # Supply Chain — software only, not logistics services
    "Supply chain management software system implementation",
    "Inventory warehouse management system software procurement",
    "Logistics management software platform deployment tender",

    # Asset Management — software only, not asset management services
    "Enterprise asset management EAM software implementation",
    "Fixed asset tracking management software procurement",
    "Asset lifecycle management system deployment tender",

    # Fleet Management
    "Fleet management software system implementation tender",
    "Vehicle fleet tracking management software procurement",
    "Transport fleet management system deployment",

    # Library Management
    "Library management system LMS software procurement",
    "Integrated library system ILS implementation tender",
    "Library automation software deployment services",

    # Finance / Accounting software — NOT financial services
    "Financial management accounting software system implementation",
    "General ledger budgeting financial software procurement",
    "Finance ERP module implementation and deployment tender",

    # Digital transformation — software projects only
    "Digital transformation enterprise software system implementation",
    "IT system modernisation enterprise software deployment",
    "Business process automation software platform procurement",
]

print("Encoding reference sentences...")
REFERENCE_EMBEDDINGS = model.encode(
    REFERENCE_SENTENCES,
    convert_to_tensor=True,
    show_progress_bar=False
)
print(f"Ready — {len(REFERENCE_SENTENCES)} reference sentences loaded")


def calculate_similarity(text: str) -> float:
    if not text or not text.strip():
        return 0.0
    try:
        embedding = model.encode(text, convert_to_tensor=True)
        scores = util.cos_sim(embedding, REFERENCE_EMBEDDINGS)[0]
        return float(torch.max(scores))
    except Exception as e:
        print(f"Embedding error: {e}")
        return 0.0


def calculate_similarity_with_reason(text: str) -> tuple:
    if not text or not text.strip():
        return 0.0, "empty text"
    try:
        embedding = model.encode(text, convert_to_tensor=True)
        scores = util.cos_sim(embedding, REFERENCE_EMBEDDINGS)[0]
        best_idx = int(torch.argmax(scores))
        best_score = float(scores[best_idx])
        best_ref = REFERENCE_SENTENCES[best_idx]
        return best_score, f'matched: "{best_ref[:60]}" ({best_score:.3f})'
    except Exception as e:
        print(f"Embedding error: {e}")
        return 0.0, f"error: {e}"