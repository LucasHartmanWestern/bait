import os
import numpy as np
from PIL import Image
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from torch.nn.functional import one_hot
import joblib
import io

# Custom dataset class for loading images and labels
class ImageDataset(Dataset):
    def __init__(self, images, product_labels, light_status_labels, transform=None):
        # Initialize dataset with images and labels
        self.images = images
        self.product_labels = product_labels
        self.light_status_labels = light_status_labels
        self.transform = transform  # Transformation to be applied on images

    def __len__(self):
        # Return the total number of samples in the dataset
        return len(self.images)

    def __getitem__(self, idx):
        # Get an image and its corresponding labels by index
        image = Image.fromarray(self.images[idx])  # Convert numpy array to PIL image
        if self.transform:
            image = self.transform(image)  # Apply transformation if any
        return image, self.product_labels[idx], self.light_status_labels[idx]

# Function to load images and extract labels from filenames
def load_images(directory):
    images = []
    product_labels = []
    light_status_labels = []
    for filename in os.listdir(directory):
        if filename.endswith('.png'):  # Check if the file is a PNG image
            image = Image.open(os.path.join(directory, filename))  # Open the image
            image = np.array(image)  # Convert the image to a numpy array
            images.append(image)
            labels = filename.split(',')  # Extract labels from the filename
            product_labels.append(labels[0].strip())
            light_status_labels.append(labels[1].strip())
    return np.array(images), np.array(product_labels), np.array(light_status_labels)

# Function to encode labels as integers
def encode_labels(labels):
    encoder = LabelEncoder()  # Create a label encoder object
    encoded_labels = encoder.fit_transform(labels)  # Fit and transform labels to integer values
    return encoded_labels, encoder

# Define the CNN architecture for product label classification
class ProductCNN(nn.Module):
    def __init__(self, num_classes):
        super(ProductCNN, self).__init__()
        # Define layers of the CNN
        self.conv1 = nn.Conv2d(3, 32, kernel_size=3)  # First convolutional layer
        self.relu = nn.ReLU()  # ReLU activation function
        self.pool = nn.MaxPool2d(2, 2)  # Max pooling layer
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3)  # Second convolutional layer
        self.flatten = nn.Flatten()  # Flatten layer to convert 2D features to 1D
        self.fc1_input_size = 64 * 56 * 56  # Calculate input size for the first fully connected layer
        self.fc1 = nn.Linear(self.fc1_input_size, 64)  # First fully connected layer
        self.fc2 = nn.Linear(64, num_classes)  # Second fully connected layer (output layer)

    def forward(self, x):
        # Define the forward pass through the network
        x = self.pool(self.relu(self.conv1(x)))  # Apply first conv layer, ReLU, and pooling
        x = self.pool(self.relu(self.conv2(x)))  # Apply second conv layer, ReLU, and pooling
        x = self.flatten(x)  # Flatten the features
        x = self.relu(self.fc1(x))  # Apply first fully connected layer and ReLU
        x = self.fc2(x)  # Apply second fully connected layer (output layer)
        return x

# Define the CNN architecture for light status classification, which takes both the image and product label as inputs
class LightStatusCNN(nn.Module):
    def __init__(self, num_product_classes, num_light_status_classes):
        super(LightStatusCNN, self).__init__()
        # Define layers of the CNN
        self.conv1 = nn.Conv2d(3, 32, kernel_size=3)  # First convolutional layer
        self.pool = nn.MaxPool2d(2, 2)  # Max pooling layer
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3)  # Second convolutional layer
        self.flatten = nn.Flatten()  # Flatten layer to convert 2D features to 1D
        self.relu = nn.ReLU()  # ReLU activation function
        self.fc1_input_size = 64 * 56 * 56 + num_product_classes  # Calculate input size for the first fully connected layer
        self.fc1 = nn.Linear(self.fc1_input_size, 64)  # First fully connected layer
        self.fc2 = nn.Linear(64, num_light_status_classes)  # Second fully connected layer (output layer)

    def forward(self, x, product_label):
        # Define the forward pass through the network
        x = self.pool(self.relu(self.conv1(x)))  # Apply first conv layer, ReLU, and pooling
        x = self.pool(self.relu(self.conv2(x)))  # Apply second conv layer, ReLU, and pooling
        x = self.flatten(x)  # Flatten the features
        x = torch.cat((x, product_label), dim=1)  # Concatenate the image features with the product label
        x = self.relu(self.fc1(x))  # Apply first fully connected layer and ReLU
        x = self.fc2(x)  # Apply second fully connected layer (output layer)
        return x

# Function to train a model
def train_model(model, dataloader, criterion, optimizer, num_epochs=10, model_type='product', total_product_classes=None):
    for epoch in range(num_epochs):
        running_loss = 0.0
        for images, product_labels, light_status_labels in dataloader:
            optimizer.zero_grad()  # Zero the gradients

            if model_type == 'product':
                outputs = model(images)  # Forward pass for product model
                labels = product_labels
            elif model_type == 'light_status':
                outputs = model(images, one_hot(product_labels, num_classes=total_product_classes))  # Forward pass for light status model
                labels = light_status_labels
            else:
                raise ValueError("Invalid model_type. Must be 'product' or 'light_status'.")

            loss = criterion(outputs, labels)  # Calculate loss
            loss.backward()  # Backward pass
            optimizer.step()  # Update weights
            running_loss += loss.item()  # Accumulate loss

        print(f'Model {model_type}, Epoch {epoch + 1}/{num_epochs}, Loss: {running_loss / len(dataloader)}')  # Print loss for each epoch

# Function to evaluate a model
def evaluate_model(model, dataloader, label_type='product', total_product_classes=None):
    correct = 0
    total = 0
    with torch.no_grad():  # Disable gradient calculation for evaluation
        for images, product_labels, light_status_labels in dataloader:
            if label_type == 'product':
                labels = product_labels
                outputs = model(images)  # Forward pass for product model
            elif label_type == 'light_status':
                labels = light_status_labels
                product_labels_one_hot = one_hot(product_labels, num_classes=total_product_classes)
                outputs = model(images, product_labels_one_hot)  # Forward pass for light status model
            else:
                raise ValueError("Invalid label_type. Must be 'product' or 'light_status'.")

            _, predicted = torch.max(outputs.data, 1)  # Get the predicted labels
            total += labels.size(0)
            correct += (predicted == labels).sum().item()  # Count correct predictions
    print(f'Model {label_type}, Accuracy: {100 * correct / total}%')  # Print accuracy

# Main function
def generate_models():
    # Load and preprocess images
    images, product_labels, light_status_labels = load_images('data/augmented')

    # Encode labels
    encoded_product_labels, product_encoder = encode_labels(product_labels)
    encoded_light_status_labels, light_status_encoder = encode_labels(light_status_labels)

    # Use the number of product classes from the encoder for consistency
    total_product_classes = len(product_encoder.classes_)

    # Split data into training and testing sets
    X_train, X_test, y_product_train, y_product_test, y_light_status_train, y_light_status_test = train_test_split(
        images, encoded_product_labels, encoded_light_status_labels, test_size=0.2, random_state=42,
        stratify=encoded_product_labels)

    # Convert labels to PyTorch tensors
    y_product_train = torch.tensor(y_product_train, dtype=torch.long)
    y_product_test = torch.tensor(y_product_test, dtype=torch.long)
    y_light_status_train = torch.tensor(y_light_status_train, dtype=torch.long)
    y_light_status_test = torch.tensor(y_light_status_test, dtype=torch.long)

    # Define image transformations
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
    ])

    # Create datasets and dataloaders
    train_dataset = ImageDataset(X_train, y_product_train, y_light_status_train, transform=transform)
    test_dataset = ImageDataset(X_test, y_product_test, y_light_status_test, transform=transform)
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)

    # Build and train the first CNN for product label classification
    product_model = ProductCNN(num_classes=len(product_encoder.classes_))
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(product_model.parameters(), lr=0.001)
    train_model(product_model, train_loader, criterion, optimizer, num_epochs=100, model_type='product')

    # Evaluate the product model
    evaluate_model(product_model, test_loader, label_type='product')

    # Build and train the second CNN for light status classification
    light_status_model = LightStatusCNN(num_product_classes=total_product_classes, num_light_status_classes=len(light_status_encoder.classes_))

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(light_status_model.parameters(), lr=0.001)
    train_model(light_status_model, train_loader, criterion, optimizer, num_epochs=100, model_type='light_status', total_product_classes=total_product_classes)

    # Evaluate the light status model
    evaluate_model(light_status_model, test_loader, label_type='light_status', total_product_classes=total_product_classes)

    # Save the trained models
    torch.save(product_model.state_dict(), 'product_model.pth')
    torch.save(light_status_model.state_dict(), 'light_status_model.pth')

    # Save the label encoders
    joblib.dump(product_encoder, 'product_encoder.joblib')
    joblib.dump(light_status_encoder, 'light_status_encoder.joblib')

def predict(image_bytestream):
    # Load the label encoders
    product_encoder = joblib.load('image classifier/product_encoder.joblib')
    light_status_encoder = joblib.load('image classifier/light_status_encoder.joblib')

    # Determine the total number of unique product classes
    total_product_classes = len(product_encoder.classes_)

    # Load the trained models
    product_model = ProductCNN(num_classes=len(product_encoder.classes_))
    product_model.load_state_dict(torch.load('image classifier/product_model.pth'))
    product_model.eval()  # Set the model to evaluation mode

    light_status_model = LightStatusCNN(num_product_classes=total_product_classes,
                                        num_light_status_classes=len(light_status_encoder.classes_))
    light_status_model.load_state_dict(torch.load('image classifier/light_status_model.pth'))
    light_status_model.eval()  # Set the model to evaluation mode

    # Preprocess the input image
    transform = transforms.Compose([
        transforms.Resize((230, 230)),
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
    ])
    image = Image.open(io.BytesIO(image_bytestream))  # Load the image from a bytestream
    image = transform(image).unsqueeze(0)  # Apply transformations and add a batch dimension

    # Predict the product label
    with torch.no_grad():  # Disable gradient calculation for prediction
        product_output = product_model(image)
        product_pred = torch.argmax(product_output, dim=1)
        product_label = product_encoder.inverse_transform([product_pred.item()])[0]

    # Predict the light status label
    with torch.no_grad():  # Disable gradient calculation for prediction
        product_label_one_hot = one_hot(product_pred, num_classes=total_product_classes)
        light_status_output = light_status_model(image, product_label_one_hot)
        light_status_pred = torch.argmax(light_status_output, dim=1)
        light_status_label = light_status_encoder.inverse_transform([light_status_pred.item()])[0]

    return product_label, light_status_label

if __name__ == '__main__':
    generate_models()