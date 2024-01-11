from transformers import BertTokenizer, BertModel
import torch
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Load pre-trained model and tokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

# Function to encode text
def encode_text(text):
    inputs = tokenizer(text, return_tensors='pt', max_length=512, truncation=True)
    outputs = model(**inputs)
    # Convert the output to NumPy array after detaching from the computation graph
    return outputs.pooler_output.squeeze().detach().numpy()

def best_match(documents, query):
    # Encode all documents and the query
    doc_embeddings = np.array([encode_text(doc) for doc in documents])
    query_embedding = encode_text(query)

    # Compute cosine similarity
    similarities = cosine_similarity([query_embedding], doc_embeddings)[0]

    # Debug prints to check shapes
    print("query", query_embedding.shape)
    print("doc", doc_embeddings.shape)

    # Rank documents based on similarity
    document_ranking = np.argsort(similarities)[::-1]

    # Display ranked documents
    print("Documents ranked by relevance:")
    for idx in document_ranking:
        print(f"Score: {similarities[idx]:.4f}, Document: {documents[idx]}")

