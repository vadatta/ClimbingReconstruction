import torch
import torch.nn as nn


CONFIG = {
    "num_epochs": 10,
    "learning_rate": 1e-3,
    "device": torch.device(
        "cuda" if torch.cuda.is_available()
        else "mps" if torch.backends.mps.is_available()
        else "cpu"
    ),
    "loss": nn.CrossEntropyLoss(),
}


def create_optimizer(model):
    return torch.optim.Adam(model.parameters(), lr=CONFIG["learning_rate"])
