from session import Session

test = Session()

res = test.search('coup detat')

res.append({
    'doc_id': 'tzun6c',
    'topic': 'arsnetioarnstie'
})

for text in res:
    print(test.read_doc(text['doc_id'])['topic'])