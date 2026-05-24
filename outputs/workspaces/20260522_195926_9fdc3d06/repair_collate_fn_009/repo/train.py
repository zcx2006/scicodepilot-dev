import sys


def collate_fn(samples):
    xs = [sample["x"] for sample in samples]
    ys = [sample["y"] for sample in samples]
    return {"features": xs, "labels": ys}


def main() -> None:
    print("Collating tiny dataset...", flush=True)
    samples = [{"x": 1, "y": 0}, {"x": 2, "y": 1}]
    batch = collate_fn(samples)

    try:
        _ = batch["x"], batch["y"]
    except KeyError as exc:
        print(
            f"KeyError: collate_fn_error: batch missing expected key {exc!s}",
            file=sys.stderr,
            flush=True,
        )
        sys.exit(1)

    print("Batch structure verified.", flush=True)


if __name__ == "__main__":
    main()
