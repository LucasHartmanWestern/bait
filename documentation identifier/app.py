if __name__ == '__main__':
    print("Running Documentation Identifier")
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')

documents = [
    "Document 1 text goes here...",
    "Document 2 text goes here...",
    # Add more documents as needed
]

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



