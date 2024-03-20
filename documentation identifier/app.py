if __name__ == '__main__':
    print("Running Documentation Identifier")

# import fitz
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from bson.binary import Binary
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords')
import pymongo
from pymongo import MongoClient
import sys  # Import sys for reading command line arguments


# def load_Documents(collection):
#     # List of paths to your PDF files
#     pdf_file_paths = [
#     'C:/Users/epigo/Documents/TempDocs/How to stay connected during a power outage to your fibre-to-the-home phone service using the Giga Hub_Home Hub 4000.pdf',
#     'C:/Users/epigo/Documents/TempDocs/Manage Bell usernames and passwords _ Bell Wi-Fi and modem administrator.pdf',
#     'C:/Users/epigo/Documents/TempDocs/Rebooting my Home Hub modem _ Reboot directly from the modem.pdf',
#     'C:/Users/epigo/Documents/TempDocs/What is the Bell Wi-Fi app and how do I use it_ _ Block or pause Internet access by user.pdf',
#     'C:/Users/epigo/Documents/TempDocs/Temporary suspensions.pdf',
#     'C:/Users/epigo/Documents/TempDocs/Bell Mobility in-store device repairs _ Repairs in a Bell store.pdf',
#     'C:/Users/epigo/Documents/TempDocs/How to use Call Blocking on my Bell Home phone.pdf',
#     'C:/Users/epigo/Documents/TempDocs/Video Equipment Installation Guides _ Bell Smart Home _ Support _ _ How to install a Bell Smart Home video doorbell.pdf',
#     'C:/Users/epigo/Documents/TempDocs/Bell Support – Security and Privacy.pdf',
#     'C:/Users/epigo/Documents/TempDocs/Bell Support – Security and Privacy_fraud.pdf',
#     'C:/Users/epigo/Documents/TempDocs/How to use my Qolsys IQ Panel security system _ How to use the Qolsys IQ Panel.pdf',
#     'C:/Users/epigo/Documents/TempDocs/How to order Pay-per-view.pdf',
#     'C:/Users/epigo/Documents/TempDocs/How do equipment returns and refunds work_ _ Return policy for Bell customers _ Return policy for Bell Mobility customers.pdf'
#
#     ]
#     # Prepare a list to hold documents
#     pdf_documents = []
#     for path in pdf_file_paths:
#         # Open each PDF file in binary read mode for binary data
#         with open(path, 'rb') as pdf_file:
#             binary_pdf = Binary(pdf_file.read())
#         # Open the PDF file with PyMuPDF for text extraction
#         doc = fitz.open(path)
#         text = ""
#         for page in doc:
#             text += page.get_text()
#
#         # Create a document including the binary data and extracted text
#         pdf_document = {
#             "name": path.split('/')[-1],  # Extract the file name from the path
#             "data": binary_pdf,
#             "text": text  # Add the extracted text
#         }
#
#         # Append the document to the list
#         pdf_documents.append(pdf_document)
#
#     # Insert the documents into your collection
#     collection.insert_many(pdf_documents)




def find_best_match(input_sentence):
    mongo_connection_string = 'mongodb+srv://ethanp:pigouEthan@cluster0.mv0wogx.mongodb.net/'
    client = MongoClient(mongo_connection_string)
    db = client['baitdb']

    questions_collection = db['conversationData']
    documents_collection = db['documentData']

    # Fetch questions and calculate similarities
    mongo_questions = questions_collection.find({})
    questions = [
        (
            doc['messages'][-1]['content'][0]['text'],
            doc['response'],
            doc.get('messages', [{'content': [{'type': 'text', 'text': 'No Query'}]}])[-1]['content'][0]['text'],
            doc.get('pdf', None)
        )
        for doc in mongo_questions if 'messages' in doc and 'response' in doc
    ]

    vectorizer_questions = TfidfVectorizer(stop_words=stopwords.words('english'))
    questions_text = [q[0] for q in questions] + [input_sentence]
    questions_vectors = vectorizer_questions.fit_transform(questions_text)
    cosine_similarities_questions = cosine_similarity(questions_vectors[-1], questions_vectors[:-1])
    if cosine_similarities_questions.size and max(cosine_similarities_questions[0]) > 0.7:
        best_question_index = cosine_similarities_questions.argmax()
        return questions[best_question_index][1]  # Assuming you want to return the response for the best matching query

    # Matching against document titles
    mongo_documents = documents_collection.find({})
    documents = [(doc['text'], doc['name'], doc.get('title', 'No Title')) for doc in mongo_documents if 'text' in doc and 'name' in doc]
    titles = [doc[2] for doc in documents]
    all_titles = titles + [input_sentence]
    vectorizer_titles = TfidfVectorizer(stop_words=stopwords.words('english'))
    titles_vectors = vectorizer_titles.fit_transform(all_titles)
    cosine_similarities_titles = cosine_similarity(titles_vectors[-1], titles_vectors[:-1])
    if max(cosine_similarities_titles[0]) > 0.9:
        best_title_index = cosine_similarities_titles.argmax()
        return documents[best_title_index][1]  # Return document name for the best title match

    # Matching against document texts if no title matches above 0.9
    texts = [doc[0] for doc in documents]
    all_texts = texts + [input_sentence]
    vectorizer_docs = TfidfVectorizer(stop_words=stopwords.words('english'))
    docs_vectors = vectorizer_docs.fit_transform(all_texts)
    cosine_similarities_docs = cosine_similarity(docs_vectors[-1], docs_vectors[:-1])
    top_match_index = cosine_similarities_docs.argsort()[0][-1]  # Get index of top match based on text similarity
    return documents[top_match_index][1]  # Return document name for the best text match


if __name__ == '__main__':
    while True:
        print("Please enter search:")
        input_sentence = input()

        if input_sentence.upper() == "EXIT":
            break
        document_name = find_best_match(input_sentence)
        print(f"Best matching document name: {document_name}")