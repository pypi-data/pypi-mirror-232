import requests

class Vectorview:
    def __init__(self, key, project_id=""):
        self.key = key
        self.project_id = project_id

    def event(self, query, docs_with_score, query_metadata=None):
        if query_metadata is None:
            query_metadata = {}

        documents = []
        for doc, score in docs_with_score:
            content = doc.page_content
            metadata = doc.metadata
            distance = score

            if "id" in metadata:
                emb_id = metadata.get('id')
            else:
                emb_id = str(hash(content))

            documents.append([content, emb_id, distance, metadata])

        payload = {
            'miko_key': self.key,
            'project_id': self.project_id,
            'query': query,
            'documents': documents,
            'metadata': query_metadata
        }

        response = requests.post('https://europe-west1-miko-17c4e.cloudfunctions.net/event', json=payload)
        return response
