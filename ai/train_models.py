import pickle
import os
from sklearn.feature_extraction.text import TfidfVectorizer

def train_and_save():
    print("Training TF-IDF model...")
    # Sample notes to act as training data
    text = """Machine learning is a subfield of artificial intelligence.
    It focuses on developing algorithms that can learn from and make predictions on data.
    These algorithms build a model based on sample inputs, known as training data.
    Deep learning is part of a broader family of machine learning methods based on artificial neural networks.
    Natural language processing enables computers to understand human language.
    TF-IDF is a statistical measure used to evaluate how important a word is to a document.
    """
    sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 5]

    # Train vectorizer
    vectorizer = TfidfVectorizer(stop_words='english')
    vectorizer.fit_transform(sentences)

    # Save model
    with open("model.pkl", "wb") as f:
        pickle.dump(vectorizer, f)

    # Save processed data sentences
    with open("data.pkl", "wb") as f:
        pickle.dump(sentences, f)

    print("Model trained and saved as model.pkl and data.pkl!")

if __name__ == "__main__":
    train_and_save()
