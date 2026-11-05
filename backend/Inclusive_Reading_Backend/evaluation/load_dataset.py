
from pathlib import Path
from huggingface_hub import hf_hub_download

DATASET_ID = "waboucay/wikilarge"

DATA_FILES = {
    "complex": "wiki.full.aner.ori.test.src",
    "simple": "wiki.full.aner.ori.test.dst",
}


def load_test_data():
    data = {}

    for column, filename in DATA_FILES.items():
        file_path = hf_hub_download(
            repo_id=DATASET_ID,
            filename=filename,
            repo_type="dataset"
        )

        with open(file_path, "r", encoding="utf-8") as file:
            data[column] = file.read().splitlines()

    if len(data["complex"]) != len(data["simple"]):
        raise ValueError("The number of complex and simple sentences does not match.")

    return data


def main():
    data = load_test_data()

    complex_sentences = data["complex"]
    simple_sentences = data["simple"]

    print("WikiLarge Test Split")
    print("-" * 40)

    print(f"Total examples: {len(complex_sentences)}")

    for i in range(min(3, len(complex_sentences))):
        print(f"\nExample {i + 1}")
        print("Complex:", complex_sentences[i])
        print("Simple:", simple_sentences[i])


if __name__ == "__main__":
    main()
