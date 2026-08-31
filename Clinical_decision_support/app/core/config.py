import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

VECTOR_DB_PATH = PROJECT_ROOT / "chroma_db"
VECTOR_DB_VECTORIZER = VECTOR_DB_PATH / "tfidf_vectorizer.pkl"
VECTOR_DB_MATRIX = VECTOR_DB_PATH / "tfidf_matrix.npz"
KNOWLEDGE_BASE_DIR = PROJECT_ROOT / "knowledge_base"
COFORGE_API_URL = os.getenv("COFORGE_API_URL")
COFORGE_API_KEY = os.getenv("COFORGE_API_KEY")
COFORGE_MODEL = os.getenv("COFORGE_MODEL", "gpt-4o")