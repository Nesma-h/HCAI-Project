
import json
from pathlib import Path

import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = BASE_DIR / "results" / "wikilarge_evaluation_results.json"

OUTPUT_CSV = BASE_DIR / "results" / "semantic_similarity_results.csv"

OUTPUT_JSON = BASE_DIR / "results" / "semantic_similarity_summary.json"

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
BATCH_SIZE = 16


def load_data():

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict):
        data = data.get("results", data.get("data", []))

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

    for col in required[1:4]:
        df[col] = df[col].fillna("").astype(str).str.strip()

    df = df[
        (df["original_text"] != "") &
        (df["reference_text"] != "") &
        (df["generated_text"] != "")
    ].copy()

    return df


def main():

    print("\n========== SEMANTIC SIMILARITY EVALUATION ==========\n")

    df = load_data()

    print("Total samples:", len(df))
    print("Loading model:", MODEL_NAME)

    model = SentenceTransformer(MODEL_NAME, device="cpu")

    original_embeddings = model.encode(
        df["original_text"].tolist(),
        batch_size=BATCH_SIZE,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    generated_embeddings = model.encode(
        df["generated_text"].tolist(),
        batch_size=BATCH_SIZE,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    reference_embeddings = model.encode(
        df["reference_text"].tolist(),
        batch_size=BATCH_SIZE,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    # Pairwise cosine similarity for matching samples
    df["source_generated_similarity"] = (
        original_embeddings * generated_embeddings
    ).sum(axis=1)

    df["generated_reference_similarity"] = (
        generated_embeddings * reference_embeddings
    ).sum(axis=1)

    summary = {
        "evaluation_name": "Semantic Similarity Evaluation",
        "dataset": "WikiLarge",
        "model": MODEL_NAME,
        "total_samples": int(len(df)),
        "average_source_generated_similarity": float(
            df["source_generated_similarity"].mean()
        ),
        "average_generated_reference_similarity": float(
            df["generated_reference_similarity"].mean()
        ),
        "median_source_generated_similarity": float(
            df["source_generated_similarity"].median()
        ),
        "median_generated_reference_similarity": float(
            df["generated_reference_similarity"].median()
        ),
        "note": (
            "Cosine similarity measures semantic embedding similarity. "
            "It does not independently prove factual preservation."
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
