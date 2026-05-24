import torch
from torch import nn


def main() -> None:
    device = torch.device("cpu")

    print("Loading synthetic classification batch...", flush=True)
    batch_size = 8
    num_classes = 3
    feature_dim = 4

    print("Computing classification loss...", flush=True)
    features = torch.randn(batch_size, feature_dim, device=device)
    classifier = nn.Linear(feature_dim, num_classes).to(device)
    logits = classifier(features)

    labels = torch.randint(0, num_classes, (batch_size + 1,), device=device)
    loss = nn.CrossEntropyLoss()(logits, labels)
    print(loss.item(), flush=True)


if __name__ == "__main__":
    main()
