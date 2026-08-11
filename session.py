from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
import csv

class Session:
    def __init__(self, ):
        self.discovered_ids = {} # read_doc will check against this to ensure that search tool is used. g
        self.TOPICS = extract_topics()
        self.DOCUMENTS, self.VECTORIZER, self.DOC_VECTORS = build_tfidf()
    
    def search(self, query: str, top_k: int = 3) -> list[dict]:
        
        query_vector = self.VECTORIZER.transform([query])
        scores = cosine_similarity(
                query_vector,
                self.DOC_VECTORS
            )[0]
            
        ranked_indices = scores.argsort()[::-1][:top_k]
            
        results = []
            
        for idx in ranked_indices:
            doc_id = list(self.DOCUMENTS.keys())[idx]
            topic = self.TOPICS[doc_id]
            
                
            results.append({
                    "doc_id": doc_id,
                    "topic": topic
            })
            
            self.discovered_ids[doc_id] = self.discovered_ids.get(doc_id, []) + [query]
            
        return results
    
    def read_doc(self, doc_id):
        
        # check if it went through actual search rigor rather than guessing.
        if doc_id not in self.discovered_ids:
            raise ValueError(f"Document ID '{doc_id}' was not prev discovered through a valid search.")
        
        return {
            "doc_id": doc_id, 
            "topic": self.TOPICS[doc_id],
            "text": self.DOCUMENTS[doc_id]
        }
        
    
def extract_topics():
 with open("./corpus/topic_tags.json", "r", encoding="utf-8") as f:
    doc_titles = json.load(f)
    mapping = {}

 with open("./corpus/mapping.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        original_id = row["original"].replace(".txt", "")
        encrypted_id = row["opaque"].replace(".txt", "")

        mapping[original_id] = encrypted_id
    
 encrypted_titles = {}

 for doc_id, topic in doc_titles.items():
    encrypted_id = mapping[doc_id]
    encrypted_titles[encrypted_id] = topic
    
 return encrypted_titles

def build_tfidf():
    CORPUS_DIR = Path("corpus/encrypted")
    
    # load docs
    documents = {}
    for file in CORPUS_DIR.glob("*.txt"):
        documents[file.stem] = file.read_text(encoding="utf-8")
        
    # build TF-IDF index
    vectorizer = TfidfVectorizer()
    doc_vectors = vectorizer.fit_transform(list(documents.values()))
    
    return (documents, vectorizer, doc_vectors)    