import json
from agents.microstructure_agent import run_microstructure_agent
from config import OUTPUT_DIR


def main():
    for paper_dir in OUTPUT_DIR.iterdir():
        sections = paper_dir / f"{paper_dir.name}_sections.json"
        if not sections.exists():
            continue

        result = run_microstructure_agent(sections)

        out = paper_dir / f"{paper_dir.name}_microstructure_agent.json"
        out.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"✅ Microstructure agent done: {paper_dir.name}")


if __name__ == "__main__":
    main()
