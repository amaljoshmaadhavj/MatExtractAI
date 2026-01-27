import json
import re
from pathlib import Path


TABLES_JSON = Path("output/Steglich_Tian_Bohlen_Kuwabara_ExpMech2014_tables.json")
OUT_JSON = Path("output/Steglich_Tian_Bohlen_Kuwabara_ExpMech2014_table1_clean.json")

TARGET_TABLE_INDEX = 9


def parse_value_with_std(text: str):
    """
    Converts values like:
    "15 (1)" -> 15
    "22.2 (1.5)" -> 22.2
    "-" -> None
    "" -> None
    """
    text = text.strip()

    if text in ["", "-", "–"]:
        return None

    # take first number before space or bracket
    match = re.search(r"[-+]?\d+(\.\d+)?", text)
    if not match:
        return None

    num = match.group()
    if "." in num:
        return float(num)
    return int(num)


def main():
    if not TABLES_JSON.exists():
        print(f"❌ Missing file: {TABLES_JSON}")
        return

    with open(TABLES_JSON, "r", encoding="utf-8") as f:
        tables = json.load(f)

    target = None
    for t in tables:
        if t["table_index"] == TARGET_TABLE_INDEX:
            target = t
            break

    if target is None:
        print(f"❌ Table index {TARGET_TABLE_INDEX} not found.")
        return

    rows = target["rows"]

    # Find header row (contains "Alloy" and "Variant")
    header_idx = None
    for i, r in enumerate(rows):
        joined = " ".join(r).lower()
        if "alloy" in joined and "variant" in joined and "tys" in joined:
            header_idx = i
            break

    if header_idx is None:
        print("❌ Could not find header row.")
        return

    header = rows[header_idx]
    data_rows = rows[header_idx + 1:]

    # Expected columns
    # Alloy | Variant | Av. grain size | TYS | CYS | SD | UTS | Fracture strain
    clean_records = []

    current_alloy = None

    for r in data_rows:
        if len(r) < 8:
            continue

        alloy = r[0].strip()
        variant = r[1].strip()

        # If alloy column is empty, it belongs to previous alloy
        if alloy != "":
            current_alloy = alloy
        else:
            alloy = current_alloy

        # skip totally empty rows
        if not alloy and not variant:
            continue

        record = {
            "alloy": alloy if alloy else None,
            "variant": variant if variant else None,
            "avg_grain_size_um": parse_value_with_std(r[2]),
            "TYS_MPa": parse_value_with_std(r[3]),
            "CYS_MPa": parse_value_with_std(r[4]),
            "SD": parse_value_with_std(r[5]),
            "UTS_MPa": parse_value_with_std(r[6]),
            "fracture_strain_pct": parse_value_with_std(r[7]),
        }

        clean_records.append(record)

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(clean_records, f, indent=2, ensure_ascii=False)

    print(f"✅ Clean Table 1 records saved to: {OUT_JSON.resolve()}")
    print(f"✅ Extracted {len(clean_records)} rows")
    print("\nSample record:")
    print(clean_records[0])


if __name__ == "__main__":
    main()