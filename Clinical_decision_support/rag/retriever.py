from rag.vector_store import collection


def retrieve_documents(query, top_k=5):
    """
    Retrieve relevant chunks from the local Chroma knowledge base.
    """

    if collection.count() == 0:
        raise FileNotFoundError("Knowledge base is empty. Please run: python build_kb.py")

    result = collection.query(query_texts=[query], n_results=top_k)
    retrieved_chunks = result.get("documents", [[]])[0]

    if not retrieved_chunks:
        return "No highly relevant context found in the current knowledge base."

    return "\n\n".join(retrieved_chunks)