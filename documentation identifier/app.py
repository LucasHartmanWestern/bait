if __name__ == '__main__':
    print("Running Documentation Identifier")

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')
import pymongo
from pymongo import MongoClient

# MongoDB's connection string
mongo_connection_string = 'mongodb+srv://<username>:<password>@<cluster-address>/<dbname>?retryWrites=true&w=majority'

# Connect to the MongoDB client
client = MongoClient(mongo_connection_string)

# Select your database
db = client['your_database_name']

# Select your collection
collection = db['your_collection_name']

# Fetch documents from MongoDB
mongo_documents = collection.find({})  # Adjust the query as needed

# Extract the text field from documents (assuming documents have a 'text' field)
documents = [doc['text'] for doc in mongo_documents]

def find_best_match(documents, input_sentence):
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
    return documents[best_match_index]

input_sentence = "Your input sentence here"
best_match = find_best_match(documents, input_sentence)
print("Best matching document:", best_match)
