
import json
import pandas as pd

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = BASE_DIR / "results"

RESULTS_FILE = RESULTS_DIR / "evaluation_results.csv"


def calculate_metrics():

    df = pd.read_csv(RESULTS_FILE)

    # Keep successful API responses only
    valid = df[
        (df["success"] == True) &
        df["generated_text"].notna()
    ].copy()

    if valid.empty:
        raise ValueError("No successful predictions found.")

    originals = valid["original_text"].astype(str).tolist()
    references = valid["reference_text"].astype(str).tolist()
    predictions = valid["generated_text"].astype(str).tolist()

    # Basic API metrics
    total = len(df)
    successful = int(df["success"].sum())
    failed = total - successful

    avg_response_time = float(
        df["response_time"].mean()
    )

    metrics = {
        "total_samples": int(total),
        "successful_requests": successful,
        "failed_requests": failed,
        "api_success_rate": round(
            successful / total * 100, 2
        ) if total else 0,
        "average_response_time_seconds": round(
            avg_response_time, 3
        )
    }

    # Readability
    try:
        import textstat

        readability_scores = [
            textstat.flesch_reading_ease(text)
            for text in predictions
        ]

        metrics["readability"] = {
            "average_flesch_reading_ease": round(
                sum(readability_scores) /
                len(readability_scores), 2
            ),
            "interpretation": (
                "Higher scores generally indicate easier reading."
            )
        }

    except ImportError:
        metrics["readability"] = "textstat not installed"

    # SARI
    try:
        import evaluate

        sari_metric = evaluate.load("sari")

        sari_result = sari_metric.compute(
            sources=originals,
            predictions=predictions,
            references=[[ref] for ref in references]
        )

        metrics["sari"] = sari_result.get("sari")

    except Exception as error:
        metrics["sari"] = None
        metrics["sari_error"] = str(error)

    # BERTScore
    try:
        from bert_score import score

        precision, recall, f1 = score(
            predictions,
            references,
            lang="en",
            verbose=False
        )

        metrics["bertscore"] = {
            "precision": round(precision.mean().item(), 4),
            "recall": round(recall.mean().item(), 4),
            "f1": round(f1.mean().item(), 4)
        }

    except Exception as error:
        metrics["bertscore"] = None
        metrics["bertscore_error"] = str(error)

    # Save metrics
    output_path = RESULTS_DIR / "metrics_summary.json"

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(
            metrics,
            file,
            ensure_ascii=False,
            indent=4
        )

    print("\n========== QUALITY EVALUATION ==========")

    for key, value in metrics.items():
        print(f"{key}: {value}")

    print(f"\nMetrics saved to: {output_path}")


if __name__ == "__main__":
    calculate_metrics()
