
import os

# Limit numerical-library threads
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import json
import pandas as pd
import sacrebleu
import textstat

from rouge_score import rouge_scorer
from evaluate import load

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(BASE_DIR, "results")

INPUT_FILE = os.path.join(
    RESULTS_DIR,
    "wikilarge_evaluation_results.csv"
)

print("Loading baseline dataset...")

df = pd.read_csv(INPUT_FILE)

print("Dataset loaded:", len(df), "samples")
print("Columns:", df.columns.tolist())

required_columns = [
    "original_text",
    "generated_text",
    "reference_text"
]

for column in required_columns:
    if column not in df.columns:
        raise ValueError(
            f"Missing required column: {column}"
        )

df = df.dropna(subset=required_columns).copy()

originals = df["original_text"].astype(str).tolist()
predictions = df["generated_text"].astype(str).tolist()
references = df["reference_text"].astype(str).tolist()

if not predictions:
    raise ValueError("No valid samples found.")

print("Valid samples:", len(predictions))

# 1. SARI
print("\nCalculating SARI...")

sari_metric = load("sari")

sari_result = sari_metric.compute(
    sources=originals,
    predictions=predictions,
    references=[[ref] for ref in references]
)

sari_score = sari_result["sari"]

# 2. BLEU
print("Calculating BLEU...")

bleu_result = sacrebleu.corpus_bleu(
    predictions,
    [references]
)

bleu_score = bleu_result.score

# 3. ROUGE-L
print("Calculating ROUGE-L...")

scorer = rouge_scorer.RougeScorer(
    ["rougeL"],
    use_stemmer=True
)

rouge_scores = []

for prediction, reference in zip(predictions, references):
    result = scorer.score(reference, prediction)
    rouge_scores.append(result["rougeL"].fmeasure)

rouge_l = sum(rouge_scores) / len(rouge_scores)

# 4. Flesch Reading Ease
print("Calculating Flesch Reading Ease...")

flesch_scores = [
    textstat.flesch_reading_ease(text)
    for text in predictions
]

flesch_average = sum(flesch_scores) / len(flesch_scores)

# Save individual results
df["flesch_reading_ease"] = flesch_scores
df["rouge_l"] = rouge_scores

individual_file = os.path.join(
    RESULTS_DIR,
    "baseline_individual_metrics.csv"
)

df.to_csv(individual_file, index=False)

# Summary
summary = {
    "dataset": "WikiLarge",
    "total_valid_samples": len(predictions),
    "SARI": sari_score,
    "BLEU": bleu_score,
    "ROUGE_L": rouge_l,
    "Flesch_Reading_Ease": flesch_average
}

summary_file = os.path.join(
    RESULTS_DIR,
    "baseline_metrics.json"
)

with open(summary_file, "w", encoding="utf-8") as file:
    json.dump(summary, file, indent=4, ensure_ascii=False)

print("\n========== BASELINE METRICS ==========")

for metric, value in summary.items():
    print(f"{metric}: {value}")

print("\nSaved files:")
print(summary_file)
print(individual_file)
