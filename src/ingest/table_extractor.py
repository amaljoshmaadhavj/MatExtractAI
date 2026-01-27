from pathlib import Path
from typing import List, Dict, Any
import pandas as pd
import camelot


def extract_tables_from_pdf(pdf_path: str | Path, pages: str = "all") -> List[Dict[str, Any]]:
    """
    Extracts tables from a PDF using Camelot.
    Returns tables as list of dicts:
    {
      "table_index": int,
      "page": int,
      "dataframe": pd.DataFrame
    }
    """
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    tables = camelot.read_pdf(str(pdf_path), pages=pages, flavor="stream")

    results = []
    for i, t in enumerate(tables):
        df = t.df
        results.append({
            "table_index": i,
            "page": t.page,
            "dataframe": df
        })

    return results


def save_tables(tables: List[Dict[str, Any]], out_dir: str | Path, base_name: str):
    """
    Saves extracted tables into CSV and JSON.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    all_tables_json = []

    for t in tables:
        idx = t["table_index"]
        page = t["page"]
        df: pd.DataFrame = t["dataframe"]

        # Save CSV for each table
        csv_path = out_dir / f"{base_name}_table_{idx}_page_{page}.csv"
        df.to_csv(csv_path, index=False, header=False)

        # Save JSON structure for each table
        table_json = {
            "table_index": idx,
            "page": page,
            "rows": df.values.tolist()
        }
        all_tables_json.append(table_json)

    # Save one combined JSON file
    json_path = out_dir / f"{base_name}_tables.json"
    import json
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_tables_json, f, indent=2, ensure_ascii=False)

    return json_path
