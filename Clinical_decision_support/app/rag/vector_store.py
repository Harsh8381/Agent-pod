import chromadb

from app.core.config import VECTOR_DB_PATH

client = chromadb.PersistentClient(
    path=str(VECTOR_DB_PATH)
)

collection = client.get_or_create_collection(
    name="medical_knowledge"
)


def store_chunks(chunks, embeddings):
    """
    Store document chunks and embeddings in ChromaDB.
    """

    ids = [str(i) for i in range(len(chunks))]

    collection.upsert(
        ids=ids,
        documents=chunks,
        embeddings=embeddings.tolist()
    )