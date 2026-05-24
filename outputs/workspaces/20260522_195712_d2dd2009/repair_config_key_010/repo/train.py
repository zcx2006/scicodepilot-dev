import sys


def main() -> None:
    print("Loading experiment configuration...", flush=True)
    config = {"learning_rate": 0.001, "epochs": 2}

    try:
        learning_rate = config["learning_rate"]
    except KeyError as exc:
        print(
            f"KeyError: config_key_error: missing experiment config key {exc!s}",
            file=sys.stderr,
            flush=True,
        )
        sys.exit(1)

    print(f"Config verified with learning_rate={learning_rate}.", flush=True)


if __name__ == "__main__":
    main()
