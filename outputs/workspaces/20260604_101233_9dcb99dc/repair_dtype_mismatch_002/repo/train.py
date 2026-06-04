import torch


def main() -> None:
    print("Loading synthetic dataset...", flush=True)
    print("Building dtype mismatch computation...", flush=True)

    x = torch.randn(4, 4, dtype=torch.float32)
    w = torch.randn(4, 4, dtype=torch.float32)

    y = x @ w
    print(y.shape, flush=True)


if __name__ == "__main__":
    main()
