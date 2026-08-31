from pathlib import Path

from pypdf import PdfReader


def load_pdf(pdf_path):
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    reader = PdfReader(str(pdf_path))
    text_parts = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text_parts.append(page_text)
    return "\n".join(text_parts)


def load_all_pdfs(folder_path):
    folder_path = Path(folder_path)
    if not folder_path.exists():
        return {}

    pdf_docs = {}
    for pdf_file in sorted(folder_path.glob("*.pdf")):
        pdf_docs[pdf_file.name] = load_pdf(pdf_file)
    return pdf_docs