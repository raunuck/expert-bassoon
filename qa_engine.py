from sentence_transformers import SentenceTransformer, util
from transformers import pipeline

# load model (downloads once, then runs locally)
model = SentenceTransformer('all-MiniLM-L6-v2')

def get_answer(question, text):
    sentences = text.split('.')
    
    embeddings = model.encode(sentences, convert_to_tensor=True)
    question_embedding = model.encode(question, convert_to_tensor=True)

    scores = util.cos_sim(question_embedding, embeddings)
    best_match = scores.argmax()

    return sentences[int(best_match)]

