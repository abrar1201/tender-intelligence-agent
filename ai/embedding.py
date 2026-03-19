from sentence_transformers import SentenceTransformer, util

# Load model once
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# Your target profile (what you want to match)
TARGET_TEXT = """
ERP implementation tender, SAP implementation, Oracle ERP,
Microsoft Dynamics 365, enterprise software deployment,
IT consulting services, system integration, digital transformation project,
cloud migration, business process automation
"""

target_embedding = model.encode(TARGET_TEXT, convert_to_tensor=True)


def calculate_similarity(text):
    if not text.strip():
        return 0

    embedding = model.encode(text, convert_to_tensor=True)

    score = util.cos_sim(embedding, target_embedding)

    return float(score)