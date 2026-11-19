
import json
import math
from pathlib import Path

import pandas as pd
import evaluate


# ==========================================
# CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "results" / "wikilarge_evaluation_results.json"

OUTPUT_CSV = BASE_DIR / "results" / "meaning_preservation_results.csv"
OUTPUT_JSON = BASE_DIR / "results" / "meaning_preservation_summary.json"


# ==========================================
# LOAD DATA
# ==========================================

def load_data():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict):
        data = data.get("results", data.get("data", []))

    if not isinstance(data, list):
        raise ValueError("Unexpected JSON structure.")

    df = pd.DataFrame(data)

    required = [
        "test_id",
        "original_text",
        "reference_text",
        "generated_text",
        "success"
    ]

    missing = [c for c in required if c not in df.columns]

    if missing:
        raise ValueError(f"Missing columns: {missing}")

    df = df[df["success"] == True].copy()

    for col in ["original_text", "reference_text", "generated_text"]:
        df[col] = df[col].fillna("").astype(str).str.strip()

    df = df[
        (df["original_text"] != "") &
        (df["reference_text"] != "") &
        (df["generated_text"] != "")
    ].copy()

    return df


# ==========================================
# SARI EVALUATION
# ==========================================

def calculate_sari(df):
    sari_metric = evaluate.load("sari")

    scores = []

    for _, row in df.iterrows():
        try:
            result = sari_metric.compute(
                sources=[row["original_text"]],
                predictions=[row["generated_text"]],
                references=[[row["reference_text"]]]
            )

            scores.append(result["sari"])

        except Exception as e:
            print(f"Failed sample {row['test_id']}: {e}")
            scores.append(None)

    return scores


# ==========================================
# MAIN
# ==========================================

def main():

    print("\n========== MEANING PRESERVATION EVALUATION ==========\n")

    df = load_data()

    print("Loaded samples:", len(df))

    df["sari_score"] = calculate_sari(df)

    valid_scores = df["sari_score"].dropna()

    summary = {
        "evaluation_name": "Meaning Preservation Evaluation",
        "dataset": "WikiLarge",
        "total_samples": int(len(df)),
        "successful_sari_samples": int(len(valid_scores)),
        "failed_sari_samples": int(df["sari_score"].isna().sum()),
        "average_sari": (
            float(valid_scores.mean()) if len(valid_scores) else None
        ),
        "median_sari": (
            float(valid_scores.median()) if len(valid_scores) else None
        ),
        "minimum_sari": (
            float(valid_scores.min()) if len(valid_scores) else None
        ),
        "maximum_sari": (
            float(valid_scores.max()) if len(valid_scores) else None
        ),
        "metric_note": (
            "SARI evaluates simplification quality using source, "
            "system output and reference. It is not a standalone "
            "measure of factual meaning preservation."
        )
    }

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4, ensure_ascii=False)

    print("\n========== RESULTS ==========")

    for key, value in summary.items():
        print(f"{key}: {value}")

    print("\nSaved CSV:", OUTPUT_CSV)
    print("Saved JSON:", OUTPUT_JSON)


if __name__ == "__main__":
    main()
