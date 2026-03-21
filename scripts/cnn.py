import torch
from torchvision.datasets import ImageFolder
from torchvision import transforms
from torch.utils.data import DataLoader, random_split
import torch.nn as nn
import torchvision.models as models


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
        std =[0.229, 0.224, 0.225]
    )
])

val_transform = transforms.Compose([
    transforms.Resize((224, 224)),

    transforms.ToTensor(),

    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std =[0.229, 0.224, 0.225]
    )
])

dataset = ImageFolder("dataset")
train_size = int(0.8 * len(dataset))
val_size = len(dataset) - train_size

train_dataset, val_dataset = random_split(dataset, [train_size, val_size])
train_dataset.dataset.transform = train_transform
val_dataset.dataset.transform = val_transform

train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=32)

class GripResNet(nn.Module):

    def __init__(self, num_classes):

        super().__init__()

        # load pretrained resnet
        self.model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)

        # freeze backbone
        for param in self.model.parameters():
            param.requires_grad = False

        # get number of features from final layer
        num_features = self.model.fc.in_features

        # replace classifier
        self.model.fc = nn.Sequential(
            nn.Linear(num_features, 128),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(128, num_classes)
        )

    def forward(self, x):

        return self.model(x)


model = GripResNet(num_classes=len(dataset.classes))
device = torch.device(
    "cuda" if torch.cuda.is_available()
    else "mps" if torch.backends.mps.is_available()
    else "cpu"
)

model = model.to(device)

criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

for epoch in range(10):

    model.train()

    for images, labels in train_loader:
        images = images.to(device)
        labels = labels.to(device)

        preds = model(images)

        loss = criterion(preds, labels)

        optimizer.zero_grad()
        loss.backward()
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

print("accuracy:", correct/total)

