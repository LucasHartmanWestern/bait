import Transformer
import BERT

if __name__ == '__main__':
    print("Running Documentation Identifier")
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords
import PyPDF2
import torch
import torch.nn as nn
nltk.download('stopwords')

pdf_file_paths = [
    "TempDocs/(4000) Rebooting my Home Hub modem _ Reboot directly from the modem.pdf",
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


def find_best_match(documents, input_sentence, file_paths):
    # Combine documents and the input sentence for vectorization
    all_docs = documents + [input_sentence]

    # Create a TF-IDF Vectorizer
    vectorizer = TfidfVectorizer(stop_words=stopwords.words('english'))

    # Vectorize the documents
    vectors = vectorizer.fit_transform(all_docs)

    # Calculate cosine similarity
    cosine_similarities = cosine_similarity(vectors[-1], vectors[:-1])

    # Find the best match
    best_match_index = cosine_similarities.argsort()[0][-1]
    return file_paths[best_match_index]



def transformerTest():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(device)

    x = torch.tensor([[1, 5, 6, 4, 3, 9, 5, 2, 0], [1, 8, 7, 3, 4, 5, 6, 7, 2]]).to(
        device
    )
    trg = torch.tensor([[1, 7, 4, 3, 5, 9, 2, 0], [1, 5, 6, 2, 4, 7, 6, 2]]).to(device)

    src_pad_idx = 0
    trg_pad_idx = 0
    src_vocab_size = 10
    trg_vocab_size = 10
    model = Transformer(src_vocab_size, trg_vocab_size, src_pad_idx, trg_pad_idx, device=device).to(
        device
    )
    out = model(x, trg[:, :-1])
    print(out.shape)


while True:
    input_sentence = input("Enter query (type exit to exit): ")

    if input_sentence.lower() == 'exit':
        break

    # best_match = find_best_match(documents, input_sentence, pdf_file_paths)
    best_match = BERT.best_match(documents, input_sentence)
    print("Best matching document:", best_match)



