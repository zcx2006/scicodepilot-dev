import sys


def main() -> None:
    print("Preparing model and batch devices...", flush=True)
    model_device = "cpu"
    input_device = "cpu"

    if model_device != input_device:
        print(
            "RuntimeError: Expected all tensors to be on the same device, but "
            "found at least two devices, cuda:0 and cpu!",
            file=sys.stderr,
            flush=True,
        )
        sys.exit(1)

    print("Device placement verified.", flush=True)


if __name__ == "__main__":
    main()
