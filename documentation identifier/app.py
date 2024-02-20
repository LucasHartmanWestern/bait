if __name__ == '__main__':
    print("Running Documentation Identifier")

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')
import pymongo
from pymongo import MongoClient
import sys  # Import sys for reading command line arguments

# MongoDB connection string
mongo_connection_string = 'mongodb+srv://<username>:<password>@<cluster-address>/<dbname>?retryWrites=true&w=majority'

# Connect to the MongoDB client
client = MongoClient(mongo_connection_string)

# Select your database
db = client['your_database_name']

# Select your collection
collection = db['your_collection_name']

# Fetch documents from MongoDB
mongo_documents = collection.find({})  # Adjust the query as needed

# Extract the text and filename from documents
documents = [(doc['text'], doc['filename']) for doc in mongo_documents]

def find_best_match(documents, input_sentence):
    # Extract just the document texts for TF-IDF vectorization
    document_texts = [doc[0] for doc in documents]

    # Combine document texts and the input sentence for vectorization
    all_docs = document_texts + [input_sentence]

    # Create a TF-IDF Vectorizer
    vectorizer = TfidfVectorizer(stop_words=stopwords.words('english'))

    # Vectorize the documents
    vectors = vectorizer.fit_transform(all_docs)

    # Calculate cosine similarity
    cosine_similarities = cosine_similarity(vectors[-1], vectors[:-1])

    # Find the best match
    best_match_index = cosine_similarities.argsort()[0][-1]

    # Return the filename of the best matching document
    return documents[best_match_index][1]

# Take input from the terminal
if len(sys.argv) > 1:
    input_sentence = sys.argv[1]  # The first command line argument
else:
    print("No input sentence provided. Exiting.")
    sys.exit()

best_match_filename = find_best_match(documents, input_sentence)
print("Best matching document filename:", best_match_filename)
