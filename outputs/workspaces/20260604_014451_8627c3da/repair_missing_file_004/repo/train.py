from pathlib import Path


def main() -> None:
    print("Loading dataset metadata...", flush=True)
    dataset_path = Path("data/train.csv")
    dataset_path.read_text(encoding="utf-8")


if __name__ == "__main__":
    main()
