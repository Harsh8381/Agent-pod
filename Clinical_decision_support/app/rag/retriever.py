import pickle
from sklearn.metrics.pairwise import cosine_similarity

from app.core.config import VECTOR_DB_MATRIX
from app.core.config import VECTOR_DB_VECTORIZER
from app.rag.vector_store import collection


def retrieve_documents(query, top_k=5):
    """
    Retrieve relevant chunks from the local Chroma knowledge base.
    """

    if collection.count() == 0:
        raise FileNotFoundError("Knowledge base is empty. Please run: python -m app.scripts.build_kb")

    if not VECTOR_DB_VECTORIZER.exists():
        raise FileNotFoundError("Knowledge-base vectorizer is missing. Please run: python -m app.scripts.build_kb")
    if not VECTOR_DB_MATRIX.exists():
        raise FileNotFoundError("Knowledge-base matrix is missing. Please run: python -m app.scripts.build_kb")

    with VECTOR_DB_VECTORIZER.open("rb") as file:
        vectorizer = pickle.load(file)

    matrix = __import__("scipy.sparse", fromlist=["load_npz"]).load_npz(VECTOR_DB_MATRIX)
    scores = cosine_similarity(vectorizer.transform([query]), matrix).ravel()
    documents = collection.get(include=["documents"]).get("documents", [])
    top_indices = scores.argsort()[::-1][:top_k]
    retrieved_chunks = [documents[index] for index in top_indices if scores[index] > 0]

    if not retrieved_chunks:
        return "No highly relevant context found in the current knowledge base."

    return "\n\n".join(retrieved_chunks)
