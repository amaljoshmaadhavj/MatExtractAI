import json
from pathlib import Path

from evaluation.validator import evaluate_record
from evaluation.cross_check import cross_check_microstructure_processing
from evaluation.confidence import aggregate_confidence


MECH = json.loads(Path("output/Steglich_Tian_Bohlen_Kuwabara_ExpMech2014_mech_agent.json").read_text())
MICRO = json.loads(Path("output/Steglich_Tian_Bohlen_Kuwabara_ExpMech2014_microstructure_agent.json").read_text())
PROC = json.loads(Path("output/Steglich_Tian_Bohlen_Kuwabara_ExpMech2014_processing_agent.json").read_text())


def main():
    evaluated = []

    for m in MICRO["microstructures"]:
        validation = evaluate_record(m)
        cross_issues = cross_check_microstructure_processing(
            m, PROC.get("processing_routes", [])
        )

        final_confidence = aggregate_confidence(validation, cross_issues)

        evaluated.append({
            "record": m,
            "validation": validation,
            "cross_agent_issues": cross_issues,
            "final_confidence": final_confidence
        })

    out = Path("output/Steglich_Tian_Bohlen_Kuwabara_ExpMech2014_evaluated.json")
    out.write_text(json.dumps(evaluated, indent=2), encoding="utf-8")

    print(f"✅ Pipeline B evaluation saved to: {out.resolve()}")


if __name__ == "__main__":
    main()
