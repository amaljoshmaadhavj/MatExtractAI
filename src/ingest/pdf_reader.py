import fitz # PyMuPDF
from pathlib import Path
from typing import Dict, Any


def extract_pdf_text_by_page(pdf_path: Path) -> Dict[str, Any]:
    doc = fitz.open(pdf_path)

    pages = []
    for i in range(doc.page_count):
        page = doc.load_page(i)
        pages.append({
            "page": i + 1,
            "text": page.get_text("text").strip()
        })

    doc.close()

    return {
        "file_name": pdf_path.name,
        "num_pages": len(pages),
        "pages": pages
    }
