import Transformer
import BERT
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords
import PyPDF2
import torch
import torch.nn as nn
nltk.download('stopwords')

pdf_file_paths = [
    "TempDocs/Rebooting my Home Hub modem _ Reboot directly from the modem.pdf",
    "TempDocs/How to stay connected during a power outage to your fibre-to-the-home phone service using the Giga Hub_Home Hub 4000.pdf",
    "TempDocs/Manage Bell usernames and passwords _ Bell Wi-Fi and modem administrator.pdf",
    "TempDocs/What is the Bell Wi-Fi app and how do I use it_ _ Block or pause Internet access by user.pdf",
    # Add more paths as needed
]

def read_pdf(file_path):
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text

documents = [read_pdf(path) for path in pdf_file_paths]

while True:
    input_sentence = input("Enter query (type exit to exit): ")
    if input_sentence.lower() == 'exit':
        break

    best_match = BERT.best_match(documents, input_sentence, pdf_file_paths)
    print("Best matching document:", best_match)
