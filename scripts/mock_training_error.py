import sys
import time


def main() -> None:
    print("Loading dataset...", flush=True)
    time.sleep(0.2)

    print("Building model...", flush=True)
    time.sleep(0.2)

    print(
        "RuntimeError: mat1 and mat2 shapes cannot be multiplied (32x64 and 128x10)",
        file=sys.stderr,
        flush=True,
    )
    sys.exit(1)


if __name__ == "__main__":
    main()
