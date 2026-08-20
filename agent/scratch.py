from session import Session
from sklearn.metrics.pairwise import cosine_similarity

s = Session()
queries = [
    'Vandhilt crowned king discovered location year discovered',
    '"Vandhilt" "discovered" "crowned king"',
    'Vandhilt discovered location crowned king year',
    '"Vandhilt" "discovered"',
    '"The Shard" discovered year',
    'Vandhilt crowned king discovered',
    '"crowned king" Vandhilt'
]
doc_ids = list(s.DOCUMENTS.keys())
target = "tosx6u"  # doc containing "The Shard was officially founded..." — confirm this is right doc for discovery fact
target_idx = doc_ids.index(target)
for q in queries:
    qv = s.VECTORIZER.transform([q])
    scores = cosine_similarity(qv, s.DOC_VECTORS)[0]
    ranked = sorted(range(len(doc_ids)), key=lambda i: -scores[i])
    rank = ranked.index(target_idx) + 1
    print(f'{q!r}: score={scores[target_idx]:.3f}, rank={rank}')