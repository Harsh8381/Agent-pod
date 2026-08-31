import pickle
from scipy.sparse import save_npz

from app.core.config import KNOWLEDGE_BASE_DIR
from app.core.config import VECTOR_DB_MATRIX
from app.core.config import VECTOR_DB_VECTORIZER
from app.rag.chunker import chunk_text
from app.rag.embeddings import generate_embeddings
from app.rag.pdf_loader import load_pdf
from app.rag.vector_store import store_chunks


def build_knowledge_base(pdf_path: str = str(KNOWLEDGE_BASE_DIR / "diseases.pdf")):
	text = load_pdf(pdf_path)
	chunks = chunk_text(text)
	vectorizer, matrix = generate_embeddings(chunks)
	store_chunks(chunks, matrix.toarray())
	with VECTOR_DB_VECTORIZER.open("wb") as file:
		pickle.dump(vectorizer, file)
	save_npz(VECTOR_DB_MATRIX, matrix)
	return len(chunks)


if __name__ == "__main__":
	print(f"Knowledge base created with {build_knowledge_base()} chunks.")
