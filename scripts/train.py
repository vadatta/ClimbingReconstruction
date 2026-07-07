import torch

from config import CONFIG, create_optimizer
from dataCleaning import create_dataloaders
from model import GripResNet


def train(model, optimizer, loss, train_loader, val_loader, num_epochs):
    device = CONFIG["device"]
    model = model.to(device)

    for _ in range(num_epochs):
        model.train()

        for images, labels in train_loader:
            images = images.to(device)
            labels = labels.to(device)

            preds = model(images)
            batch_loss = loss(preds, labels)

            optimizer.zero_grad()
            batch_loss.backward()
            optimizer.step()

        print("epoch complete")

    correct = 0
    total = 0

    model.eval()

    with torch.no_grad():
        for images, labels in val_loader:
            images = images.to(device)
            labels = labels.to(device)

            preds = model(images)
            predicted = preds.argmax(dim=1)

            correct += (predicted == labels).sum().item()
            total += labels.size(0)

    accuracy = correct / total if total else 0
    print("accuracy:", accuracy)

    return accuracy


if __name__ == "__main__":
    train_loader, val_loader, classes = create_dataloaders()
    model = GripResNet(num_classes=len(classes))
    optimizer = create_optimizer(model)

    train(
        model=model,
        optimizer=optimizer,
        loss=CONFIG["loss"],
        train_loader=train_loader,
        val_loader=val_loader,
        num_epochs=CONFIG["num_epochs"]
    )
