from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
import csv


CORPUS_DIR = Path("corpus/encrypted")


#helper function
def extract_topics():
 with open("./corpus/topic_tags.json", "r", encoding="utf-8") as f:
    doc_titles = json.load(f)
    print(doc_titles["doc_1"])
    mapping = {}

 with open("./corpus/mapping.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        original_id = row["original"].replace(".txt", "")
        encrypted_id = row["opaque"].replace(".txt", "")

        mapping[original_id] = encrypted_id
    print(mapping["doc_1"])
    
 encrypted_titles = {}

 for doc_id, topic in doc_titles.items():
    encrypted_id = mapping[doc_id]
    encrypted_titles[encrypted_id] = topic
    
 return encrypted_titles

TOPICS = extract_topics()

def search(query: str, top_k: int = 3) -> list[dict]:
    """
    Returns up to top_k documents ranked by relevance to query.
    Each result: {"doc_id": "a3f9k2", "topic": [pre written topics for each document]}
    Does NOT return full document text.
    """
    # load docs
    documents = {}
    for file in CORPUS_DIR.glob("*.txt"):
        documents[file.stem] = file.read_text(encoding="utf-8")
        
    # build TF-IDF index
    doc_ids = list(documents.keys())
    doc_texts = list(documents.values())
    vectorizer = TfidfVectorizer()
    doc_vectors = vectorizer.fit_transform(doc_texts)
    
    # search
    query_vector = vectorizer.transform([query])
    
    scores = cosine_similarity(
        query_vector,
        doc_vectors
    )[0]
    
    ranked_indices = scores.argsort()[::-1][:top_k]
    
    results = []
    
    for idx in ranked_indices:
        doc_id = doc_ids[idx]
        topic = TOPICS[doc_id]
        

        results.append({
            "doc_id": doc_id,
            "topic": topic
        })

    return results

print(search("coup d'état"))