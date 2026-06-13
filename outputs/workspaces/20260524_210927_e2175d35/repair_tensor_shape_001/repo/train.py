import torch
from torch import nn


def main() -> None:
    device = torch.device("cpu")

    print("Loading synthetic dataset...", flush=True)
    batch_size = 32
    upstream_feature_dim = 64
    x = torch.randn(batch_size, upstream_feature_dim, device=device)

    print("Building tiny classifier head...", flush=True)
    classifier_expected_dim = 128
    num_classes = 10
    classifier = nn.Linear(classifier_expected_dim, num_classes).to(device)

    # This benchmark intentionally wires a 64-wide tensor into a layer that
    # expects 128 features, so PyTorch raises the real RuntimeError.
    logits = classifier(x)
    print(logits.shape, flush=True)


if __name__ == "__main__":
    main()
