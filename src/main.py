import json
from pathlib import Path
from tqdm import tqdm

from ingest.pdf_reader import extract_pdf_text_by_page
from ingest.section_splitter import split_into_sections
from ingest.table_extractor import extract_tables_from_pdf, save_tables


RAW_PDF_DIR = Path("data/raw_pdfs")
OUTPUT_DIR = Path("output")


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    pdf_files = list(RAW_PDF_DIR.glob("*.pdf"))

    if not pdf_files:
        print(f"❌ No PDF files found in: {RAW_PDF_DIR.resolve()}")
        print("➡️ Please add at least one PDF inside data/raw_pdfs/")
        return

    print(f"✅ Found {len(pdf_files)} PDF(s) in {RAW_PDF_DIR.resolve()}\n")

    for pdf_path in tqdm(pdf_files, desc="Processing PDFs"):
        print(f"\n📄 Processing: {pdf_path.name}")

        # ✅ Step 1: Extract page-wise text
        extracted = extract_pdf_text_by_page(pdf_path)
        out_page_text_file = OUTPUT_DIR / f"{pdf_path.stem}_page_text.json"
        with open(out_page_text_file, "w", encoding="utf-8") as f:
            json.dump(extracted, f, indent=2, ensure_ascii=False)

        # ✅ Step 2: Split into sections
        full_text = "\n\n".join([p["text"] for p in extracted["pages"]])
        sections = split_into_sections(full_text)
        out_sections_file = OUTPUT_DIR / f"{pdf_path.stem}_sections.json"
        with open(out_sections_file, "w", encoding="utf-8") as f:
            json.dump(sections, f, indent=2, ensure_ascii=False)

        # ✅ Step 3: Extract tables
        print("📌 Extracting tables (Camelot)...")
        try:
            tables = extract_tables_from_pdf(pdf_path, pages="all")
            json_path = save_tables(tables, OUTPUT_DIR, pdf_path.stem)
            print(f"✅ Saved extracted tables JSON: {json_path.resolve()}")
            print(f"✅ Extracted {len(tables)} table(s)")
        except Exception as e:
            print("⚠️ Table extraction failed:", e)

    print("\n🎉 Done!")


if __name__ == "__main__":
    main()
