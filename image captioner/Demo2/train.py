import torch
import torch.nn as nn
import torch.optim as optim
import torchvision.transforms as transforms
from torch.utils.tensorboard import SummaryWriter
from utils import save_checkpoint, load_checkpoint, print_examples, test_model_on_images
from get_loader import get_loader, Vocabulary
from model import CNNtoRNN, CustomLoss
import os
import signal
import sys
from torch.optim.lr_scheduler import StepLR, ReduceLROnPlateau


# Handles exiting the training loop
def signal_handler(sig, frame):
    print('You pressed Ctrl+C! Exiting gracefully.')
    sys.exit(0)

# Register the signal handler
signal.signal(signal.SIGINT, signal_handler)

# Main training loop
def train():
    combined_transforms = transforms.Compose([
        # Augmentation transformations
        transforms.Resize(299),
        transforms.ColorJitter(brightness=0.5, contrast=0.5, saturation=0.5, hue=0.1),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomRotation(degrees=15),
        transforms.RandomAffine(degrees=0, translate=(0.1, 0.1)),
        transforms.RandomResizedCrop(299, scale=(0.8, 1.0), ratio=(0.75, 1.33)),
        # Standard transformations
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
    ])

    train_loader, dataset = get_loader(
        root_folder="document/images",
        annotation_file="document/captions.txt",
        transform=combined_transforms,
        num_workers=2,
    )

    # Try to use GPU to train
    torch.backends.cudnn.benchmark = True
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    # Choose whether to save/load model during training iterations
    load_model = False
    save_model = True

    # Hyperparameters
    embed_size = 512 #256
    hidden_size = 512 #256
    vocab_size = len(dataset.vocab)
    num_layers = 3
    learning_rate = 5e-4 #3e-4
    num_epochs = 100 #1004
    

    # Used to check the vocabulary
    def print_vocabulary(vocab):
        for idx, word in vocab.itos.items():
            print(f'Vocab: {idx}: {word}')
    #print_vocabulary(dataset.vocab)

    # For tensorboard
    writer = SummaryWriter("runs/flickr")
    step = 0

    # Initialize model
    model = CNNtoRNN(embed_size, hidden_size, vocab_size, num_layers).to(device)
    #criterion = nn.CrossEntropyLoss(ignore_index=dataset.vocab.stoi["<PAD>"])
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    # 1.0 to disable
    #scheduler = StepLR(optimizer, step_size=10, gamma=1.0)
    scheduler = ReduceLROnPlateau(optimizer, 'min', factor=0.1, patience=10, verbose=True)  

    PAD_IDX = dataset.vocab.stoi["<PAD>"]
    UNK_IDX = dataset.vocab.stoi["<UNK>"]
    criterion = CustomLoss(pad_idx=PAD_IDX, unk_idx=UNK_IDX, unk_penalty_lambda=5.0)

    # Load model from previous weights
    if load_model:
        step = load_checkpoint(torch.load("my_checkpoint.pth.tar"), model, optimizer)
        print(f"Loading checkpoint. Resuming from step {step}")
    else:
        print('Not loading')

    # Start the training loop
    model.train()

    PAD_IDX = dataset.vocab.stoi["<PAD>"]  

    for epoch in range(num_epochs):
        print(f"Epoch: {epoch + 1}/{num_epochs}")
        test_model_on_images(model, device, ["test_examples/bylaws.png", "test_examples/contract.png", "test_examples/privacy.jpg"], dataset)

        if save_model:
            checkpoint = {
                "state_dict": model.state_dict(),
                "optimizer": optimizer.state_dict(),
                "step": step,
                "vocab": dataset.vocab,
            }
            save_checkpoint(checkpoint)
            torch.save(checkpoint, "my_checkpoint.pth")
            Vocabulary.save_vocab(dataset.vocab, "vocab.pkl")
            
        total_loss = 0.0
        for idx, (imgs, captions) in enumerate(train_loader):
            imgs = imgs.to(device)
            captions = captions.to(device)

            optimizer.zero_grad()
            outputs = model(imgs, captions[:, :-1])
            targets = captions[:, 1:].reshape(-1)

            # Reshape outputs for loss calculation
            outputs = outputs.reshape(-1, outputs.shape[2])

            # Create a mask for non-padding values
            mask = targets != PAD_IDX
            outputs_filtered = outputs[mask]
            targets_filtered = targets[mask]

            # Calculate loss using only the non-padded values
            #loss = criterion(outputs_filtered, targets_filtered)
            loss = criterion(outputs, targets.reshape(-1))
            total_loss += loss.item()

            writer.add_scalar("Training loss", loss.item(), global_step=step)
            step += 1

            loss.backward()
            optimizer.step()

        average_loss = total_loss / len(train_loader)
        scheduler.step(average_loss)
        print(f"Average Loss for Epoch {epoch + 1}: {average_loss}")

        print(f"Current Learning Rate: {optimizer.param_groups[0]['lr']}")

if __name__ == "__main__":
    train()
