import torch
import torch.nn as nn
import torch.optim as optim
import torchvision.transforms as transforms
from torch.utils.tensorboard import SummaryWriter
from utils import save_checkpoint, load_checkpoint, print_examples
from get_loader import get_loader, Vocabulary
from model import CNNtoRNN

def train():
    transform = transforms.Compose([
    transforms.Resize((356, 356)),
    transforms.RandomCrop((299, 299)),
    transforms.ToTensor(),
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
])


    train_loader, dataset = get_loader(
        root_folder="flickr8k/images",
        annotation_file="flickr8k/captions.txt",
        transform=transform,
        num_workers = 2,
    )

    torch.backends.cudnn.benchmark = True
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    load_model = False
    save_model = True

    #Hyperparameters
    embed_size = 256
    hidden_size = 256
    vocab_size = len(dataset.vocab)
    num_layers = 1
    learning_rate = 3e-4
    num_epochs = 100

    # for tensorboard
    writer = SummaryWriter("runs/flickr")
    step=0

    # initialize model
    model = CNNtoRNN(embed_size, hidden_size, vocab_size, num_layers).to(device)
    criterion = nn.CrossEntropyLoss(ignore_index=dataset.vocab.stoi["<PAD>"])
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    load_model = True
    if load_model:
        step = load_checkpoint(torch.load("my_checkpoint.pth.tar"), model, optimizer)
        print(f"loading checkpoint. Resuming from step {step}")
    else:
        print('not loading')


    model.train()

    def save_model(model, path='model.pkl'):
        torch.save(model, path)

    for epoch in range(num_epochs):
        #print out which epoch the model is currently on
        print(f"Epoch: {epoch + 1}/{num_epochs}")
        print_examples(model, device, dataset)
        if save_model:
            checkpoint = {
                "state_dict" : model.state_dict(),
                "optimizer" : optimizer.state_dict(),
                "step" : step,
                "vocab": dataset.vocab,
            }
            save_checkpoint(checkpoint)
            torch.save(checkpoint, "my_checkpoint.pth")
            Vocabulary.save_vocab(dataset.vocab, "vocab.pkl")
            
        total_loss = 0.0
        for idx, (imgs, captions) in enumerate(train_loader):
            imgs = imgs.to(device)
            captions = captions.to(device)

            outputs = model(imgs, captions[:-1])
            loss = criterion(outputs.reshape(-1, outputs.shape[2]), captions.reshape(-1))
            total_loss += loss.item()

            writer.add_scalar("Training loss", loss.item(), global_step=step)
            step += 1

            optimizer.zero_grad()
            loss.backward(loss)
            optimizer.step()

        average_loss = total_loss / len(train_loader)
        print(f"Average Loss for Epoch {epoch + 1}: {average_loss}")

if __name__ == "__main__":
    train()


