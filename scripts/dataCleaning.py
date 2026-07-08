import torch
from torch.utils.data import DataLoader, Subset, random_split
from torchvision import transforms
from torchvision.datasets import ImageFolder

from config import CONFIG


def create_train_transform(rotation_degrees=None, gaussian_blur_kernel=None):
    rotation_degrees = CONFIG["rotation_degrees"] if rotation_degrees is None else rotation_degrees
    gaussian_blur_kernel = (
        CONFIG["gaussian_blur_kernel"]
        if gaussian_blur_kernel is None
        else gaussian_blur_kernel
    )

    transform_steps = [
        transforms.Resize((224, 224)),
        transforms.RandomRotation(rotation_degrees),
        transforms.ColorJitter(
            brightness=0.2,
            contrast=0.2,
            saturation=0.2,
            hue=0.05
        ),
    ]

    if gaussian_blur_kernel:
        transform_steps.append(transforms.GaussianBlur(gaussian_blur_kernel))

    transform_steps.extend([
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])

    return transforms.Compose(transform_steps)


train_transform = create_train_transform()

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


def create_train_val_split(
    dataset,
    train_ratio=0.8,
    rotation_degrees=None,
    gaussian_blur_kernel=None,
    seed=None
):
    train_size = int(train_ratio * len(dataset))
    val_size = len(dataset) - train_size
    generator = torch.Generator().manual_seed(seed) if seed is not None else None

    train_indices, val_indices = random_split(
        range(len(dataset)),
        [train_size, val_size],
        generator=generator
    )

    train_dataset = ImageFolder(
        dataset.root,
        transform=create_train_transform(rotation_degrees, gaussian_blur_kernel)
    )
    val_dataset = ImageFolder(dataset.root, transform=val_transform)

    return Subset(train_dataset, train_indices.indices), Subset(val_dataset, val_indices.indices)


def create_dataloaders(
    dataset_path="dataset",
    batch_size=None,
    train_ratio=None,
    rotation_degrees=None,
    gaussian_blur_kernel=None,
    seed=None
):
    batch_size = CONFIG["batch_size"] if batch_size is None else batch_size
    train_ratio = CONFIG["train_ratio"] if train_ratio is None else train_ratio
    seed = CONFIG["seed"] if seed is None else seed

    dataset = load_dataset(dataset_path)
    train_dataset, val_dataset = create_train_val_split(
        dataset,
        train_ratio,
        rotation_degrees,
        gaussian_blur_kernel,
        seed
    )

    generator = torch.Generator().manual_seed(seed) if seed is not None else None
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        generator=generator
    )
    val_loader = DataLoader(val_dataset, batch_size=batch_size)

    return train_loader, val_loader, dataset.classes
