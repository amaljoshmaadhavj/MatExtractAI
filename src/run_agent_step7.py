import json
from pathlib import Path
from agents.processing_agent import run_processing_agent


SECTIONS = Path("output/Steglich_Tian_Bohlen_Kuwabara_ExpMech2014_sections.json")
OUTFILE = Path("output/Steglich_Tian_Bohlen_Kuwabara_ExpMech2014_processing_agent.json")


def main():
    data = run_processing_agent(SECTIONS)

    OUTFILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"✅ Processing Agent output saved to: {OUTFILE.resolve()}")


if __name__ == "__main__":
    main()