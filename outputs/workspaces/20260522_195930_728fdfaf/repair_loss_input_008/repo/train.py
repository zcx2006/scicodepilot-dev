import sys


def main() -> None:
    print("Preparing logits and targets...", flush=True)
    target_kind = "probabilities"

    if target_kind != "class_indices":
        print(
            "ValueError: loss_input_error: CrossEntropyLoss expected class index "
            "targets, but received probability-like targets.",
            file=sys.stderr,
            flush=True,
        )
        sys.exit(1)

    print("Loss inputs verified.", flush=True)


if __name__ == "__main__":
    main()
