import fitz  # PyMuPDF
from pathlib import Path
from typing import Dict, Any


def extract_pdf_text_by_page(pdf_path: str | Path) -> Dict[str, Any]:
    """
    Extracts page-wise text from a PDF using PyMuPDF.
    Returns a structured dictionary to be saved as JSON.
    """
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found at: {pdf_path}")

    doc = fitz.open(pdf_path)

    pages = []
    for i in range(doc.page_count):
        page = doc.load_page(i)
        text = page.get_text("text")  # plain text
        pages.append({
            "page": i + 1,
            "text": text.strip()
        })

    result = {
        "file_name": pdf_path.name,
        "file_path": str(pdf_path),
        "num_pages": doc.page_count,
        "pages": pages
    }

    doc.close()
    return result