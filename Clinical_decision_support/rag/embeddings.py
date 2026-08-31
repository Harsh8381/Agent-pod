from sentence_transformers import SentenceTransformer
import numpy as np


embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


def generate_embeddings(texts):
    """
    Generate embeddings for document chunks.
    Used while building the knowledge base.
    """
    embeddings = embedding_model.encode(
        texts,
        convert_to_numpy=True
    )

    return embeddings.astype("float32")


def generate_query_embedding(query):
    """
    Generate embedding for user query or patient summary.
    Used during retrieval.
    """
    embedding = embedding_model.encode(
        query,
        convert_to_numpy=True
    )

    return embedding.astype("float32").tolist()