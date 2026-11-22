
import os

# Limit numerical library threads
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import json
import pandas as pd
import numpy as np

from evaluate import load
from sacrebleu import corpus_bleu
from rouge_score import rouge_scorer
import textstat

INPUT = "evaluation/results/wikilarge_evaluation_results.csv"

OUTPUT_CSV = "evaluation/results/baseline_metrics.csv"
OUTPUT_JSON = "evaluation/results/baseline_metrics.json"

df = pd.read_csv(INPUT)

required = [
    "original_text",
    "generated_text",
    "reference_text"
]

for col in required:
    if col not in df.columns:
        raise ValueError(f"Missing column: {col}")

df = df.dropna(subset=required).copy()

for col in required:
    df[col] = df[col].astype(str).str.strip()

df = df[
    (df["original_text"] != "") &
    (df["generated_text"] != "") &
    (df["reference_text"] != "")
].copy()

if len(df) == 0:
    raise ValueError("No valid samples available.")

predictions = df["generated_text"].tolist()
references = df["reference_text"].tolist()

print("Valid samples:", len(df))

# 1. SARI
print("Calculating SARI...")
sari_metric = load("sari")

sari_result = sari_metric.compute(
    sources=df["original_text"].tolist(),
    predictions=predictions,
    references=[[ref] for ref in references]
)

sari_score = sari_result["sari"]

# 2. Flesch Reading Ease
print("Calculating Flesch Reading Ease...")

flesch_scores = [
    textstat.flesch_reading_ease(text)
    for text in predictions
]

avg_flesch = float(np.mean(flesch_scores))

# 3. BLEU
print("Calculating BLEU...")

bleu_result = corpus_bleu(
    predictions,
    [references]
)

bleu_score = float(bleu_result.score)

# 4. ROUGE-L
print("Calculating ROUGE-L...")

scorer = rouge_scorer.RougeScorer(
    ["rougeL"],
    use_stemmer=True
)

rouge_scores = []

for pred, ref in zip(predictions, references):
    score = scorer.score(ref, pred)
    rouge_scores.append(score["rougeL"].fmeasure)

avg_rouge = float(np.mean(rouge_scores))

# Results
results = {
    "dataset": "WikiLarge",
    "total_valid_samples": len(df),
    "metrics": {
        "SARI": float(sari_score),
        "Flesch_Reading_Ease": avg_flesch,
        "BLEU": bleu_score,
        "ROUGE_L": avg_rouge
    }
}

# Save individual scores
df["flesch_reading_ease"] = flesch_scores
df["rouge_l"] = rouge_scores

df.to_csv(OUTPUT_CSV, index=False)

with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=4, ensure_ascii=False)

print("\n========== BASELINE METRICS ==========")
print(json.dumps(results, indent=4))
print("\nSaved:", OUTPUT_CSV)
print("Saved:", OUTPUT_JSON)
