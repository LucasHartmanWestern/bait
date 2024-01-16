from transformers import BertTokenizer, BertModel
import torch
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Load pre-trained model and tokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

def encode_text(text):
    inputs = tokenizer(text, return_tensors='pt', max_length=512, truncation=True)
    outputs = model(**inputs)
    return outputs.pooler_output.squeeze().detach().numpy()

def best_match(documents, query, document_paths):
    # Process each document's content for embeddings
    doc_embeddings = np.array([encode_text(doc) for doc in documents])
    query_embedding = encode_text(query)

    # Compute cosine similarity
    similarities = cosine_similarity([query_embedding], doc_embeddings)[0]

    # Rank documents based on similarity
    document_ranking = np.argsort(similarities)[::-1]

    # Display ranked document file paths with relevancy scores
    print("Documents ranked by relevance:")
    for idx in document_ranking:
        doc_path = document_paths[idx]  # Retrieve the file path of the document
        print(f"Score: {similarities[idx]:.4f}, Document Path: {doc_path}")

    # Return the file path of the most relevant document
    best_match_index = document_ranking[0]
    return document_paths[best_match_index]
