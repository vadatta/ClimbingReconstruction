from torch.utils.data import DataLoader, Subset, random_split
from torchvision import transforms
from torchvision.datasets import ImageFolder


train_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ColorJitter(
        brightness=0.2,
        contrast=0.2,
        saturation=0.2,
        hue=0.05
    ),
    transforms.GaussianBlur(3),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

val_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


def load_dataset(dataset_path="dataset"):
    return ImageFolder(dataset_path)


def create_train_val_split(dataset, train_ratio=0.8):
    train_size = int(train_ratio * len(dataset))
    val_size = len(dataset) - train_size

    train_indices, val_indices = random_split(range(len(dataset)), [train_size, val_size])

    train_dataset = ImageFolder(dataset.root, transform=train_transform)
    val_dataset = ImageFolder(dataset.root, transform=val_transform)

    return Subset(train_dataset, train_indices.indices), Subset(val_dataset, val_indices.indices)


def create_dataloaders(dataset_path="dataset", batch_size=32, train_ratio=0.8):
    dataset = load_dataset(dataset_path)
    train_dataset, val_dataset = create_train_val_split(dataset, train_ratio)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size)

    return train_loader, val_loader, dataset.classes
