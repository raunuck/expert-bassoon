from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

def extract_keywords(text, top_n=5):
    """
    Extract top keywords from a text using TF-IDF.
    """
    vectorizer = TfidfVectorizer(stop_words='english')
    try:
        tfidf_matrix = vectorizer.fit_transform([text])
    except ValueError:
        return []
    
    feature_names = vectorizer.get_feature_names_out()
    scores = np.asarray(tfidf_matrix.sum(axis=0)).flatten()
    
    # Sort by score
    sorted_indices = scores.argsort()[::-1]
    
    keywords = [feature_names[idx] for idx in sorted_indices[:top_n]]
    return keywords

if __name__ == "__main__":
    sample_text = "Machine learning is a subfield of artificial intelligence. It focuses on developing algorithms that can learn from and make predictions on data. These algorithms build a model based on sample inputs, known as training data, in order to make data-driven predictions or decisions expressed as outputs, rather than following strictly static program instructions."
    print("--- Keyword Extraction ---")
    print(extract_keywords(sample_text))
