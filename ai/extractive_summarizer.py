import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import networkx as nx

def summarize_text(text, num_sentences=3):
    """
    Extractive text summarization using TF-IDF and TextRank.
    This model extracts the most important sentences from the text.
    """
    sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 5]
    if len(sentences) <= num_sentences:
        return text

    # Create TF-IDF matrix
    vectorizer = TfidfVectorizer(stop_words='english')
    try:
        tfidf_matrix = vectorizer.fit_transform(sentences)
    except ValueError:
        return text # Handle cases with empty or stopword-only text
    
    # Calculate similarity matrix
    similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)
    
    # Use PageRank algorithm to rank sentences
    nx_graph = nx.from_numpy_array(similarity_matrix)
    scores = nx.pagerank(nx_graph)
    
    # Sort sentences by score
    ranked_sentences = sorted(((scores[i], s) for i, s in enumerate(sentences)), reverse=True)
    
    # Extract top sentences
    summary = '. '.join([s for _, s in ranked_sentences[:num_sentences]]) + '.'
    return summary

if __name__ == "__main__":
    sample_text = "Machine learning is a subfield of artificial intelligence. It focuses on developing algorithms that can learn from and make predictions on data. These algorithms build a model based on sample inputs, known as training data, in order to make data-driven predictions or decisions expressed as outputs, rather than following strictly static program instructions. The study of mathematical optimization delivers methods, theory and application domains to the field of machine learning."
    print("--- Extractive Summary ---")
    print(summarize_text(sample_text, 2))
