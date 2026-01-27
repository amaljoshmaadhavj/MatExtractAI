import json
from pathlib import Path

TABLES_JSON = Path("output/Steglich_Tian_Bohlen_Kuwabara_ExpMech2014_tables.json")

def main():
    if not TABLES_JSON.exists():
        print(f"❌ Tables JSON not found: {TABLES_JSON}")
        return

    with open(TABLES_JSON, "r", encoding="utf-8") as f:
        tables = json.load(f)

    print(f"✅ Total tables found: {len(tables)}\n")

    for t in tables:
        idx = t["table_index"]
        page = t["page"]
        rows = t["rows"]

        # Print only first few rows to preview
        preview_rows = rows[:6]

        print("=" * 80)
        print(f"📌 Table Index: {idx} | Page: {page}")
        print("Preview (first 6 rows):")

        for r in preview_rows:
            print(r)

if __name__ == "__main__":
    main()