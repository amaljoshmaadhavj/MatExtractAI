from pathlib import Path
from typing import List, Dict, Any
import pandas as pd
import camelot


def extract_tables_from_pdf(pdf_path: Path, pages: str = "all") -> List[Dict[str, Any]]:
    tables = camelot.read_pdf(str(pdf_path), pages=pages, flavor="stream")

    results = []
    for i, t in enumerate(tables):
        results.append({
            "table_index": i,
            "page": t.page,
            "rows": t.df.values.tolist()
        })

    return results
