
import pandas as pd
import json
import time
from pathlib import Path
from api_client import simplify_text

BASE_DIR = Path(__file__).resolve().parent.parent

DATASET_PATH = BASE_DIR / "dataset" / "wikilarge_hf_test.csv"
RESULTS_DIR = BASE_DIR / "results"

RESULTS_DIR.mkdir(parents=True, exist_ok=True)

CSV_OUTPUT = RESULTS_DIR / "wikilarge_evaluation_results.csv"
JSON_OUTPUT = RESULTS_DIR / "wikilarge_evaluation_results.json"


def save_results(results):
    results_df = pd.DataFrame(results)

    results_df.to_csv(
        CSV_OUTPUT,
        index=False,
        encoding="utf-8-sig"
    )

    with open(JSON_OUTPUT, "w", encoding="utf-8") as file:
        json.dump(
            results,
            file,
            ensure_ascii=False,
            indent=4
        )


def run_evaluation():

    df = pd.read_csv(DATASET_PATH)

    required_columns = [
        "test_id",
        "original_text",
        "reference_text"
    ]

    for column in required_columns:
        if column not in df.columns:
            raise ValueError(f"Missing column: {column}")

    df = df.dropna(subset=required_columns).copy()

    for column in required_columns:
        df[column] = df[column].astype(str).str.strip()

    df = df[
        (df["test_id"] != "") &
        (df["original_text"] != "") &
        (df["reference_text"] != "")
    ].copy()

    # Load previous checkpoint if available
    results_by_id = {}

    if CSV_OUTPUT.exists():
        previous_df = pd.read_csv(
            CSV_OUTPUT,
            dtype={"test_id": str}
        )

        for record in previous_df.to_dict("records"):
            results_by_id[str(record["test_id"])] = record

        print("Previous results loaded:", len(results_by_id))

    total = len(df)

    print("\n" + "=" * 50)
    print("WIKILARGE API EVALUATION")
    print("Total samples:", total)
    print("=" * 50)

    try:

        for index, row in enumerate(df.itertuples(index=False), start=1):

            test_id = str(row.test_id)
            original = row.original_text
            reference = row.reference_text

            # Skip already successful samples
            previous = results_by_id.get(test_id)

            if (
                previous
                and str(previous.get("success")).lower() == "true"
                and isinstance(previous.get("generated_text"), str)
                and previous["generated_text"].strip()
            ):
                print(
                    f"Skipping {index}/{total} | "
                    f"{test_id} | Already completed"
                )
                continue

            print(
                f"\nProcessing {index}/{total} | ID: {test_id}"
            )

            start_time = time.time()

            api_result = simplify_text(
                original,
                timeout=120
            )

            response_time = round(
                time.time() - start_time,
                3
            )

            generated = (
                api_result.get("generated_text")
                or api_result.get("simplified_text")
            )

            result = {
                "test_id": test_id,
                "original_text": original,
                "reference_text": reference,
                "generated_text": generated,
                "success": api_result.get("success", False),
                "status_code": api_result.get("status_code"),
                "response_time": response_time,
                "error": api_result.get("error")
            }

            # Update or insert result
            results_by_id[test_id] = result

            # Save after EVERY sample
            ordered_results = [
                results_by_id[str(item.test_id)]
                for item in df.itertuples(index=False)
                if str(item.test_id) in results_by_id
            ]

            save_results(ordered_results)

            print("Success:", result["success"])
            print("Status:", result["status_code"])
            print("Response time:", response_time, "seconds")

            if not result["success"]:
                print("Error:", result["error"])

    except KeyboardInterrupt:
        print("\n\nEvaluation interrupted by user.")
        print("Saving completed results...")

    # Final checkpoint
    ordered_results = [
        results_by_id[str(item.test_id)]
        for item in df.itertuples(index=False)
        if str(item.test_id) in results_by_id
    ]

    save_results(ordered_results)

    successful = sum(
        str(item["success"]).lower() == "true"
        and isinstance(item.get("generated_text"), str)
        and item["generated_text"].strip()
        for item in ordered_results
    )

    failed = len(ordered_results) - successful
    pending = total - len(ordered_results)

    print("\n" + "=" * 50)
    print("EVALUATION SUMMARY")
    print("=" * 50)

    print("Dataset samples:", total)
    print("Processed samples:", len(ordered_results))
    print("Successful:", successful)
    print("Failed:", failed)
    print("Pending:", pending)

    if ordered_results:
        print(
            "API success rate:",
            round(successful / len(ordered_results) * 100, 2),
            "%"
        )

        avg_time = sum(
            float(item.get("response_time") or 0)
            for item in ordered_results
        ) / len(ordered_results)

        print("Average response time:", round(avg_time, 3))

    print("\nResults saved:")
    print(CSV_OUTPUT)
    print(JSON_OUTPUT)


if __name__ == "__main__":
    run_evaluation()
