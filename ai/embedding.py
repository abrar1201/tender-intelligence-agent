from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")

PROFILE = """

ERP implementation
SAP
Oracle ERP
Microsoft Dynamics
enterprise systems
digital transformation
system integrator

"""

profile_embedding = model.encode(PROFILE, convert_to_tensor=True)


def calculate_similarity(text):

    if not text:
        return 0

    emb = model.encode(text, convert_to_tensor=True)

    score = float(util.cos_sim(profile_embedding, emb))

    return score