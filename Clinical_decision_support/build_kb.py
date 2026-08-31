import argparse

from core.config import KNOWLEDGE_BASE_DIR
from rag.pdf_loader import load_pdf
from rag.chunker import chunk_text
from rag.embeddings import generate_embeddings
from rag.vector_store import store_chunks


def build_knowledge_base(pdf_path):
	text = load_pdf(pdf_path)
	chunks = chunk_text(text)
	embeddings = generate_embeddings(chunks)
	store_chunks(chunks, embeddings)
	return len(chunks)


def main():
	parser = argparse.ArgumentParser(description="Build the clinical knowledge base from a PDF.")
	parser.add_argument("pdf_path", nargs="?", default=str(KNOWLEDGE_BASE_DIR / "diseases.pdf"))
	args = parser.parse_args()
	print(f"Knowledge base created with {build_knowledge_base(args.pdf_path)} chunks.")


if __name__ == "__main__":
	main()