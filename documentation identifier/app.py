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


mongo_connection_string = 'mongodb+srv://<username>:<password>@cluster0.mv0wogx.mongodb.net/'

# Connect to the MongoDB client
client = MongoClient(mongo_connection_string)

# Select your database
db = client['baitdb']

# Select your collection
collection = db['ethanData']

# Fetch documents from MongoDB
mongo_documents = collection.find({})  # Adjust the query as needed

# Extract the text and filename from documents
documents = [(doc['text'], doc['title']) for doc in mongo_documents if 'text' in doc]

def find_best_match(documents, input_sentence):
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
    top_match_indices = similarities.argsort()[0][-10:]

    # Reverse the indices since argsort returns in ascending order and we want the top matches
    top_match_indices = top_match_indices[::-1]

    # Retrieve the filenames and scores for the top three matches
    top_matches = [(documents[index][1], similarities[0, index]) for index in top_match_indices]

    return top_matches

while(True):
    print("Please enter search:")
    input_sentence = input()  # Ask for input interactively

    if input_sentence.upper() == "EXIT":
        break

    top_matches = find_best_match(documents, input_sentence)

    print("Top 3 matching documents:")
    for filename, score in top_matches:
        print(f"Filename: {filename}, Similarity Score: {score}")
