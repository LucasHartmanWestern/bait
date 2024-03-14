if __name__ == '__main__':
    print("Running Documentation Identifier")

import fitz
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from bson.binary import Binary
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords')
import pymongo
from pymongo import MongoClient
import sys  # Import sys for reading command line arguments


def load_Documents(collection):
    # List of paths to your PDF files
    pdf_file_paths = [
    'C:/Users/epigo/Documents/TempDocs/How to stay connected during a power outage to your fibre-to-the-home phone service using the Giga Hub_Home Hub 4000.pdf',
    'C:/Users/epigo/Documents/TempDocs/Manage Bell usernames and passwords _ Bell Wi-Fi and modem administrator.pdf',
    'C:/Users/epigo/Documents/TempDocs/Rebooting my Home Hub modem _ Reboot directly from the modem.pdf',
    'C:/Users/epigo/Documents/TempDocs/What is the Bell Wi-Fi app and how do I use it_ _ Block or pause Internet access by user.pdf',
    'C:/Users/epigo/Documents/TempDocs/Temporary suspensions.pdf',
    'C:/Users/epigo/Documents/TempDocs/Bell Mobility in-store device repairs _ Repairs in a Bell store.pdf',
    'C:/Users/epigo/Documents/TempDocs/How to use Call Blocking on my Bell Home phone.pdf',
    'C:/Users/epigo/Documents/TempDocs/Video Equipment Installation Guides _ Bell Smart Home _ Support _ _ How to install a Bell Smart Home video doorbell.pdf',
    'C:/Users/epigo/Documents/TempDocs/Bell Support – Security and Privacy.pdf',
    'C:/Users/epigo/Documents/TempDocs/Bell Support – Security and Privacy_fraud.pdf',
    'C:/Users/epigo/Documents/TempDocs/How to use my Qolsys IQ Panel security system _ How to use the Qolsys IQ Panel.pdf',
    'C:/Users/epigo/Documents/TempDocs/How to order Pay-per-view.pdf',
    'C:/Users/epigo/Documents/TempDocs/How do equipment returns and refunds work_ _ Return policy for Bell customers _ Return policy for Bell Mobility customers.pdf'

    ]
    # Prepare a list to hold documents
    pdf_documents = []
    for path in pdf_file_paths:
        # Open each PDF file in binary read mode for binary data
        with open(path, 'rb') as pdf_file:
            binary_pdf = Binary(pdf_file.read())
        # Open the PDF file with PyMuPDF for text extraction
        doc = fitz.open(path)
        text = ""
        for page in doc:
            text += page.get_text()

        # Create a document including the binary data and extracted text
        pdf_document = {
            "name": path.split('/')[-1],  # Extract the file name from the path
            "data": binary_pdf,
            "text": text  # Add the extracted text
        }

        # Append the document to the list
        pdf_documents.append(pdf_document)

    # Insert the documents into your collection
    collection.insert_many(pdf_documents)




def find_best_match(input_sentence):
    mongo_connection_string = 'mongodb+srv://ethanp:pigouEthan@cluster0.mv0wogx.mongodb.net/'

    # Connect to the MongoDB client
    client = MongoClient(mongo_connection_string)

    # Select your database
    db = client['baitdb']

    collection = db['documentData']

    # Fetch documents from MongoDB
    mongo_documents = collection.find({})  # Adjust the query as needed

    # Extract the text and filename from documents
    documents = [(doc['text'], doc['name']) for doc in mongo_documents if 'text' in doc]

    # Separate titles and texts from documents
    titles = [doc[1] for doc in documents]  # Titles
    texts = [doc[0] for doc in documents]  # Texts

    # Add input_sentence as a title for vectorization
    all_titles = titles + [input_sentence]

    # Create a TF-IDF Vectorizer for titles
    vectorizer_title = TfidfVectorizer(stop_words=stopwords.words('english'))
    vectors_title = vectorizer_title.fit_transform(all_titles)

    # Calculate cosine similarity for titles
    cosine_similarities_title = cosine_similarity(vectors_title[-1], vectors_title[:-1])

    # Check if any title similarity is above 90%
    max_similarity_title = max(cosine_similarities_title[0])

    if max_similarity_title < 0.90:
        # If no title similarity is above 90%, proceed with texts
        all_texts = texts + [input_sentence]
        vectorizer_text = TfidfVectorizer(stop_words=stopwords.words('english'))
        vectors_text = vectorizer_text.fit_transform(all_texts)
        cosine_similarities_text = cosine_similarity(vectors_text[-1], vectors_text[:-1])
        similarities = cosine_similarities_text
    else:
        similarities = cosine_similarities_title

    # Find the indices of the top three matches based on the selected similarity measure
    top_match_indices = similarities.argsort()[0][-3:]

    # Reverse the indices since argsort returns in ascending order and we want the top matches
    top_match_indices = top_match_indices[::-1]

    # Retrieve the filenames and scores for the top three matches
    top_matches = [(documents[index][1], similarities[0, index]) for index in top_match_indices]

    return top_matches


while (True):
    print("Please enter search:")
    input_sentence = input()  # Ask for input interactively

    if input_sentence.upper() == "EXIT":
        break

    top_matches = find_best_match(input_sentence)

    print("Top 3 matching documents:")
    for filename, score in top_matches:
        print(f"Filename: {filename}, Similarity Score: {score}")
