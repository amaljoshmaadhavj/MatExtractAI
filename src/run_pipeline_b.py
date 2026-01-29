import json
from evaluation.validator import evaluate_record
from config import OUTPUT_DIR


def main():
    for paper_dir in OUTPUT_DIR.iterdir():
        micro = paper_dir / f"{paper_dir.name}_microstructure_agent.json"
        if not micro.exists():
            continue

        records = json.loads(micro.read_text())

        validated = []
        for r in records["microstructures"]:
            validated.append({
                "record": r,
                "validation": evaluate_record(r)
            })

        out = paper_dir / f"{paper_dir.name}_validated.json"
        out.write_text(json.dumps(validated, indent=2), encoding="utf-8")

        print(f"✅ Pipeline B done: {paper_dir.name}")


if __name__ == "__main__":
    main()
