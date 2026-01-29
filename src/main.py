import json
from pathlib import Path
from tqdm import tqdm

from config import RAW_PDF_DIR, OUTPUT_DIR
from ingest.pdf_reader import extract_pdf_text_by_page
from ingest.section_splitter import split_sections
from ingest.table_extractor import extract_tables_from_pdf


def main():
    pdfs = list(RAW_PDF_DIR.glob("*.pdf"))

    if not pdfs:
        print("❌ No PDFs found in data/raw_pdfs")
        return

    for pdf_path in tqdm(pdfs, desc="Processing PDFs"):
        paper_name = pdf_path.stem
        paper_out = OUTPUT_DIR / paper_name
        paper_out.mkdir(parents=True, exist_ok=True)

        print(f"\n📄 Processing {paper_name}")

        pdf_text = extract_pdf_text_by_page(pdf_path)
        sections = split_sections(pdf_text)
        tables = extract_tables_from_pdf(pdf_path)

        with open(paper_out / f"{paper_name}_sections.json", "w", encoding="utf-8") as f:
            json.dump(sections, f, indent=2, ensure_ascii=False)

        with open(paper_out / f"{paper_name}_tables.json", "w", encoding="utf-8") as f:
            json.dump(tables, f, indent=2, ensure_ascii=False)

        print(f"✅ Saved outputs to {paper_out}")


if __name__ == "__main__":
    main()
