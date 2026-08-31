from sklearn.feature_extraction.text import TfidfVectorizer


def create_vectorizer():
    """
    Create TF-IDF vectorizer for local semantic-like text retrieval.
    This avoids Hugging Face, Gemini, and external model downloads.
    """
    return TfidfVectorizer(
        stop_words="english",
        max_features=5000,
        ngram_range=(1, 2)
    )


def generate_embeddings(texts):
    """
    Kept for compatibility with build_kb.py.
    Returns TF-IDF matrix and vectorizer.
    """
    vectorizer = create_vectorizer()
    matrix = vectorizer.fit_transform(texts)

    return vectorizer, matrix
