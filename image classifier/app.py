import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import torch.nn.functional as F  # Import the functional API
from torchvision import datasets, transforms
from PIL import Image
import os

# Hyperparameters and parameters
epochs = 10 # training epochs
lr = 0.01 # learning rate
momentum = 0.9 # training momentum
use_custom_images = False
num_of_outputs = 10
save_model = True
load_model = False


class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        in_channels = 3 if use_custom_images else 1
        self.conv1 = nn.Conv2d(in_channels, 32, 3, 1)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(32, 64, 3, 1)
        self.fc1 = nn.Linear(64 * 5 * 5, num_of_outputs)  # Updated to correct dimensions

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = torch.flatten(x, 1)  # Flattening the tensor for the fully connected layer
        x = self.fc1(x)
        return x

class CustomDataset(Dataset):
    def __init__(self, root_dir, transform=None):
        self.root_dir = root_dir
        self.transform = transform
        self.images = []
        self.labels = []
        self.classes = os.listdir(root_dir)  # Assumes each subdirectory represents a class
        self.class_to_idx = {cls_name: i for i, cls_name in enumerate(self.classes)}

        for cls in self.classes:
            cls_dir = os.path.join(root_dir, cls)
            for file in os.listdir(cls_dir):
                if file.endswith('.jpg') or file.endswith('.png'):
                    self.images.append(os.path.join(cls_dir, file))
                    self.labels.append(self.class_to_idx[cls])

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        img_path = self.images[idx]
        image = Image.open(img_path).convert('RGB')
        label = self.labels[idx]
        if self.transform:
            image = self.transform(image)
        return image, label

def get_custom_dataloader():

    transform = transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    train_dataset = CustomDataset(root_dir='data/train', transform=transform)
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)

    val_dataset = CustomDataset(root_dir='data/val', transform=transform)
    val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)

    test_dataset = CustomDataset(root_dir='data/test', transform=transform)
    test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)

    return train_loader

def download_dataset():
    print("Downloading Dataset")

    # Load and preprocess the data
    transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.5,), (0.5,))])
    trainset = datasets.MNIST(root='./data', train=True, download=True, transform=transform)
    trainloader = torch.utils.data.DataLoader(trainset, batch_size=64, shuffle=True)
    return trainloader

def train_model(use_custom_images=True):

    if use_custom_images:
        trainloader = get_custom_dataloader()
    else:
        trainloader = download_dataset()

    # Define the neural network

    model = Net()

    # Define loss function and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(model.parameters(), lr=lr, momentum=momentum)

    print("Begin Training")
    epoch_losses = []  # List to store loss per epoch

    # Train the model
    if not use_custom_images:
        for epoch in range(epochs):
            total_loss = 0.0
            for i, data in enumerate(trainloader, 0):
                inputs, labels = data
                optimizer.zero_grad()
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                loss.backward()
                optimizer.step()
                total_loss += loss.item()  # Add batch loss

            average_loss = total_loss / len(trainloader)  # Calculate average loss
            epoch_losses.append(average_loss)  # Store loss for this epoch
            print(f"Epoch {epoch + 1}, Average Loss: {average_loss}")
    else:
        for epoch in range(epochs):
            total_loss = 0.0
            for inputs, labels in trainloader:
                optimizer.zero_grad()
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                loss.backward()
                optimizer.step()
                total_loss += loss.item()  # Add batch loss

            average_loss = total_loss / len(trainloader)  # Calculate average loss
            epoch_losses.append(average_loss)  # Store loss for this epoch
            print(f"Epoch {epoch + 1}, Average Loss: {average_loss}")

    print('Finished Training')

    if save_model:
        torch.save(model.state_dict(), 'model.pth')

    return model, transforms

def predict_image(image_path, model, transform):
    image = Image.open(image_path).convert('RGB')
    image = transform(image)
    image = image.unsqueeze(0)  # Add batch dimension

    output = model(image)
    _, predicted = torch.max(output.data, 1)
    return predicted

if __name__ == '__main__':
    print("Initialize Model")

    if load_model:
        model = Net()  # Make sure this is the same architecture as the one you saved
        model.load_state_dict(torch.load('model.pth'))
    else:
        model, transform = train_model(use_custom_images)

    # Example usage
    model.eval()  # Set the model to evaluation mode
    prediction = predict_image('path/to/new/image.jpg', model, transform)