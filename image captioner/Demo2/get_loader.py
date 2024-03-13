import os  
import pandas as pd 
import spacy  
import torch
from torch.nn.utils.rnn import pad_sequence  
from torch.utils.data import DataLoader, Dataset
from PIL import Image 
import torchvision.transforms as transforms
import pickle
import easyocr


# Download with: python -m spacy download en
# Used for tokenization
spacy_eng = spacy.load("en_core_web_sm")

# EasyOCR used to read text from the images
reader = easyocr.Reader(['en'])

# Creates the vocabulary in which the captions are generated from
# Uses a frequency threshold that adds to vocab based on word frequency
class Vocabulary:
    def __init__(self, freq_threshold):
        self.itos = {0: "<PAD>", 1: "<SOS>", 2: "<EOS>", 3: "<UNK>"}
        self.stoi = {"<PAD>": 0, "<SOS>": 1, "<EOS>": 2, "<UNK>": 3}
        self.freq_threshold = freq_threshold
        self.frequencies = {} 

    def __len__(self):
        return len(self.itos)

    @staticmethod
    def tokenizer_eng(text):
        # Changes english text into a list of word tokens
        return [tok.text.lower() for tok in spacy_eng.tokenizer(text.lower())]

    # Builds the vocabulary based on frequency of words in the sentence list
    def build_vocabulary(self, sentence_list):
        frequencies = {}
        idx = 4

        keywords = [
            'document', 'education', 'non-disclosure', 'agreement', 'privacy', 'router', 'configuration', 'network', 'question', 'answer',
            'greece', 'eligibility', 'vaccination', 'schooling', 'temporary sites', 'urban settings', 'confidentiality', 'parties',
            'information', 'ownership', 'law', 'secure', 'passwords', 'date', 'time', 'settings', 'IP', 'routing', 'RIP', 'version', 'network',
            'auto-summary', 'rental', 'term', 'premises', 'occupancy', 'rent', 'payment', 'security deposit', 'commission', 'principal', 'agent',
            'sales', 'pricing', 'promotional', 'geographical areas', 'consumer', 'relations', 'efficiency', 'cost', 'customer service',
            'contact', 'bylaws', 'structure', 'compliance', 'registered agent', 'corporate seal', 'legal', 'adoption', 'policy', 'consent',
            'personal information', 'PIPEDA', 'data collection', 'interaction', 'website', 'business', 'contract', 'services', 'purchase price',
            'payment schedule', 'delivery', 'risk of loss', 'security interest', 'obligations'
        ]


        for keyword in keywords:
            frequencies[keyword] = self.freq_threshold

            # Build frequency dictionary
        for sentence in sentence_list:
            for word in self.tokenizer_eng(sentence):
                if word not in frequencies:
                    frequencies[word] = 1
                else:
                    frequencies[word] += 1
        
        self.frequencies = frequencies
        # Add words to vocabulary if they meet the frequency threshold

        for word, freq in frequencies.items():
            if freq >= self.freq_threshold or word in keywords:
                self.stoi[word] = idx
                self.itos[idx] = word
                idx += 1


        if frequencies:
            self.most_common_word = max(frequencies, key=frequencies.get)

    

    # Converts the text into a sequence of numbers
    def numericalize(self, text):
        tokenized_text = self.tokenizer_eng(text)

        return [
            self.stoi[token] if token in self.stoi else self.stoi["<UNK>"]
            for token in tokenized_text
        ]
    
    # Function to save vocabulary to a pkl file, used for portability of the model
    @staticmethod
    def save_vocab(vocab, path):
        with open(path, 'wb') as f:
            pickle.dump(vocab, f)

    # Function to load the vocabulary from the pkl file
    @staticmethod
    def load_vocab(path):
        with open(path, 'rb') as f:
            vocab = pickle.load(f)
        return vocab

# Used for image captioning, takes in a custom document dataset using OCR
class FlickrDatasetWithOCR(Dataset):
    def __init__(self, root_dir, captions_file, transform=None, freq_threshold=1):
        self.root_dir = root_dir
        self.df = pd.read_csv(captions_file)
        self.transform = transform
        self.vocab = Vocabulary(freq_threshold)

        ocr_texts = [self.extract_text(os.path.join(self.root_dir, img_name)) for img_name in self.df['image']]
        all_texts = self.df['caption'].tolist() + ocr_texts
        self.vocab.build_vocabulary(all_texts)

    def extract_text(self, img_path):
        #Use EasyOCR to extract text from an image
        text = " ".join([detection[1].lower() for detection in reader.readtext(img_path)])
        # Used to check what happens after data augmentation
        print(f"OCR result for {img_path}: {text}") 
        return text

    # Number of items in the dataset
    def __len__(self):
        return len(self.df)

    # Returns the image and its caption
    def __getitem__(self, index):
        image_name = self.df.iloc[index, 0]
        img_path = os.path.join(self.root_dir, image_name)
        img = Image.open(img_path).convert("RGB")


        # Apply transformations
        if self.transform:
            img = self.transform(img)

        # Convert caption to lowercase
        caption = self.df.iloc[index, 1].lower()  
        
        numericalized_caption = [self.vocab.stoi["<SOS>"]] + self.vocab.numericalize(caption) + [self.vocab.stoi["<EOS>"]]
        
        return img, torch.tensor(numericalized_caption)

# Data preparation 
class MyCollate:
    def __init__(self, pad_idx):
        self.pad_idx = pad_idx

    def __call__(self, batch):
        imgs = [item[0].unsqueeze(0) for item in batch]
        imgs = torch.cat(imgs, dim=0)
        targets = [item[1] for item in batch]
        targets = pad_sequence(targets, batch_first=False, padding_value=self.pad_idx)

        return imgs, targets

# Used to load the dataset
def get_loader(root_folder, annotation_file, transform, batch_size=32, num_workers=8, shuffle=True, pin_memory=True):

    dataset = FlickrDatasetWithOCR(root_folder, annotation_file, transform=augmentation_transforms, freq_threshold=2)

    pad_idx = dataset.vocab.stoi["<PAD>"]

    loader = DataLoader(dataset=dataset, batch_size=batch_size, num_workers=num_workers, shuffle=shuffle, pin_memory=pin_memory, collate_fn=MyCollate(pad_idx))

    return loader, dataset

# Apply data transformations
standard_transforms = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),  # Assuming you want to keep normalization
])

augmentation_transforms = transforms.Compose([
    transforms.Resize(299),  # Ensure this is enough to keep images at least 299x299
    transforms.ColorJitter(brightness=0.5, contrast=0.5, saturation=0.5, hue=0.1),
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.RandomRotation(degrees=15),
    transforms.RandomAffine(degrees=0, translate=(0.1, 0.1)),
    transforms.RandomResizedCrop(299, scale=(0.8, 1.0), ratio=(0.75, 1.33)),
    transforms.ToTensor(),
])

# Order when transformations are applied
combined_transforms = transforms.Compose([
    # Apply augmentation transformations first
    *augmentation_transforms.transforms,
    # Apply standard transformations (resizing and converting to tensor)
    *standard_transforms.transforms,
])


if __name__ == "__main__":
    loader, dataset = get_loader(
        "document/images/",
        "document/captions.txt",
        # Switch to standard, combines or augmented at will
        transform=combined_transforms,
        batch_size=32,
        num_workers=8,
        shuffle=True,
        pin_memory=True,
    )

    for idx, (imgs, captions) in enumerate(loader):
        print(imgs.shape)
        print(captions.shape)