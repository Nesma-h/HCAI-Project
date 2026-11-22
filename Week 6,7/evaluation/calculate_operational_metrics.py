
import os
import json
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(BASE_DIR, "results")

INPUT_FILE = os.path.join(
    RESULTS_DIR,
    "wikilarge_evaluation_results.csv"
)

df = pd.read_csv(INPUT_FILE)

# Convert response time to numeric
df["response_time"] = pd.to_numeric(
    df["response_time"],
    errors="coerce"
)

# Handle success values
success = df["success"].astype(str).str.lower().isin(
    ["true", "1", "yes"]
)

times = df["response_time"].dropna()

summary = {
    "total_requests": int(len(df)),
    "successful_requests": int(success.sum()),
    "failed_requests": int((~success).sum()),
    "success_rate_percent": round(
        success.mean() * 100, 2
    ),
    "average_response_time": round(times.mean(), 4),
    "median_response_time": round(times.median(), 4),
    "p95_response_time": round(times.quantile(0.95), 4),
    "min_response_time": round(times.min(), 4),
    "max_response_time": round(times.max(), 4)
}

output_file = os.path.join(
    RESULTS_DIR,
    "baseline_operational_metrics.json"
)

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=4)

print("========== OPERATIONAL METRICS ==========")

for key, value in summary.items():
    print(f"{key}: {value}")

print("\nSaved:", output_file)
