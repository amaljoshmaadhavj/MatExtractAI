import json
from pathlib import Path
from agents.mechanical_properties_agent import run_mechanical_properties_agent
from config import OUTPUT_DIR


def main():
    for paper_dir in OUTPUT_DIR.iterdir():
        if not paper_dir.is_dir():
            continue

        paper = paper_dir.name
        table1 = paper_dir / f"{paper}_table1_clean.json"
        sections = paper_dir / f"{paper}_sections.json"

        if not table1.exists():
            continue

        result = run_mechanical_properties_agent(table1, sections)

        out = paper_dir / f"{paper}_mech_agent.json"
        out.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"✅ Mechanical agent done: {paper}")


if __name__ == "__main__":
    main()
