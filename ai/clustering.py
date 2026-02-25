from sklearn.cluster import KMeans
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

def cluster_tenders(tenders):
    texts = [t["description"] for t in tenders]
    embeddings = model.encode(texts)

    kmeans = KMeans(n_clusters=3)
    labels = kmeans.fit_predict(embeddings)

    for i, tender in enumerate(tenders):
        tender["cluster"] = int(labels[i])

    return tenders
