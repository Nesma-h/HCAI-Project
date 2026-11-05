
import json
from pathlib import Path

import evaluate

BASE_DIR = Path(__file__).parent
INPUT_FILE = BASE_DIR / "results" / "model_outputs.json"
OUTPUT_FILE = BASE_DIR / "results" / "sari_results.json"


def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        results = json.load(file)

    if not results:
        raise ValueError("No model outputs found.")

    sources = [item["complex"] for item in results]
    predictions = [item["prediction"] for item in results]

    # SARI expects a list of reference lists.
    references = [
        [item["reference"]]
        for item in results
    ]

    sari = evaluate.load("sari")

    scores = sari.compute(
        sources=sources,
        predictions=predictions,
        references=references
    )

    output = {
        "model": "gemini-3.5-flash-lite",
        "dataset": "WikiLarge Test Split",
        "evaluated_examples": len(results),
        "sari_score": scores["sari"]
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(output, file, ensure_ascii=False, indent=4)

    print("SARI Evaluation Results")
    print("-" * 35)
    print(f"Evaluated examples: {len(results)}")
    print(f"SARI Score: {scores['sari']:.2f}")
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
