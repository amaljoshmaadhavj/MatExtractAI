import json
from pathlib import Path
from agents.mechanical_properties_agent import run_mechanical_properties_agent


TABLE1 = Path("output/Steglich_Tian_Bohlen_Kuwabara_ExpMech2014_table1_clean.json")
SECTIONS = Path("output/Steglich_Tian_Bohlen_Kuwabara_ExpMech2014_sections.json")
OUTFILE = Path("output/Steglich_Tian_Bohlen_Kuwabara_ExpMech2014_mech_agent.json")


def main():
    data = run_mechanical_properties_agent(TABLE1, SECTIONS)

    OUTFILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"✅ Agent output saved to: {OUTFILE.resolve()}")


if __name__ == "__main__":
    main()