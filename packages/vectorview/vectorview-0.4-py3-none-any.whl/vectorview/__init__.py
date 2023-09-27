import requests

class Vectorview:
    def __init__(self, key, project_id="default"):
        self.key = key
        self.project_id = project_id

    def event(self, query, docs_with_score, query_metadata=None):
        if query_metadata is None:
            query_metadata = {}

        documents = []
        for doc, score in docs_with_score:
            documents.append({
                "text": doc.page_content,
                "distance": score,
                "metadata": doc.metadata
                })

        payload = {
            'vv_key': self.key,
            'project_id': self.project_id,
            'query': query,
            'documents': documents,
            'metadata': query_metadata
        }

        response = requests.post('https://europe-west1-miko-17c4e.cloudfunctions.net/event', json=payload)
        return response
