
import json
import random
from pathlib import Path

from load_dataset import load_test_data

SAMPLE_SIZE = 30
RANDOM_SEED = 42

OUTPUT_DIR = Path(__file__).parent / "results"
OUTPUT_FILE = OUTPUT_DIR / "evaluation_sample.json"


def main():
    data = load_test_data()

    examples = [
        {
            "id": index,
            "complex": complex_text,
            "reference": simple_text
        }
        for index, (complex_text, simple_text)
        in enumerate(zip(data["complex"], data["simple"]), start=1)
    ]

    random.seed(RANDOM_SEED)
    sample = random.sample(
        examples,
        min(SAMPLE_SIZE, len(examples))
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(sample, file, ensure_ascii=False, indent=4)

    print(f"Total test examples: {len(examples)}")
    print(f"Selected sample: {len(sample)}")
    print(f"Saved to: {OUTPUT_FILE}")

    print("\nFirst selected example:")
    print("Complex:", sample[0]["complex"])
    print("Reference:", sample[0]["reference"])


if __name__ == "__main__":
    main()
