import torch
from PIL import Image
import torchvision.transforms as transforms
import spacy
import pickle
#from model import CNNtoRNN  
import easyocr 
import io
import base64
#---------------------------------------------------------------------------------------


#MAKE SURE TO READ 'requirements.txt' AND INSTALL ALL REQUIRED DEPENDENCIES


#---------------------------------------------------------------------------------------


'''
def load_vocab(path):
    with open(path, 'rb') as f:
        vocab = pickle.load(f)
    return vocab

def load_model(model_path, vocab_size, embed_size=512, hidden_size=512, num_layers=3):
    model = CNNtoRNN(embed_size, hidden_size, vocab_size, num_layers)
    checkpoint = torch.load(model_path, map_location=torch.device('cpu'))  
    state_dict = checkpoint['state_dict']
    model.load_state_dict(state_dict)
    model.eval() 
    return model


transform = transforms.Compose([
    transforms.Resize((299, 299)),
    transforms.ToTensor(),
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
])

def generate_caption_from_byte_stream(byte_stream, model, vocab):
    image = Image.open(io.BytesIO(byte_stream)).convert("RGB")
    image = transform(image).unsqueeze(0)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    image = image.to(device)
    model = model.to(device)
    caption_output = model.caption_image(image, vocab, max_length=50)
    caption_text = ' '.join([vocab.itos.get(idx, '<UNK>') for idx in caption_output if idx not in (vocab.stoi['<PAD>'], vocab.stoi['<SOS>'], vocab.stoi['<EOS>'])])
    return caption_text
'''

def print_easyocr_text_from_byte_stream(byte_stream):
    reader = easyocr.Reader(['en'])
    results = reader.readtext(byte_stream)
    ocr_text = ' '.join([text for _, text, _ in results])
    return ocr_text


#---------------------------------------------------------------------------------------
'''
# paste the name of the .pth file here for the trained weights
model_path = 'my_checkpoint.pth'
# paste the name of the .pkl file here for the vocabulary
vocab_path ='vocab.pkl'
vocab = load_vocab(vocab_path)
vocab_size = len(vocab)

model = load_model(model_path, vocab_size)
'''
#---------------------------------------------------------------------------------------
def process_image(byte_stream):
    # Split the string to get the Base64 part
    base64_str = byte_stream.split(",")[-1]

    # Decode Base64 to get the byte stream
    image_bytes = base64.b64decode(base64_str)

    # Extract text using EasyOCR from the byte stream
    ocr_text = print_easyocr_text_from_byte_stream(image_bytes)
    return ocr_text