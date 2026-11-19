
import json
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "dataset" / "wikilarge_test.json"
OUTPUT_FILE = BASE_DIR / "dataset" / "wikilarge_hf_test.csv"

with open(INPUT_FILE, "r", encoding="utf-8") as file:
    data = json.load(file)

df = pd.DataFrame(data)

# Validate required columns
required = ["complex", "simple", "test_id"]

for column in required:
    if column not in df.columns:
        raise ValueError(f"Missing column: {column}")

# Remove invalid rows only
df = df.dropna(subset=required).copy()

for column in ["complex", "simple", "test_id"]:
    df[column] = df[column].astype(str).str.strip()

df = df[
    (df["complex"] != "")
    & (df["simple"] != "")
    & (df["test_id"] != "")
].copy()

# Rename columns for the existing evaluation runner
df = df.rename(columns={
    "complex": "original_text",
    "simple": "reference_text"
})

# Preserve test IDs
df = df[[
    "test_id",
    "original_text",
    "reference_text"
]]

df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)

print("========== DATASET PREPARATION ==========")
print("Total samples:", len(df))
print("Columns:", list(df.columns))
print("Unique IDs:", df["test_id"].nunique())
print("CSV saved at:", OUTPUT_FILE)

print("\nFirst 3 samples:")
print(df.head(3).to_string(index=False))
