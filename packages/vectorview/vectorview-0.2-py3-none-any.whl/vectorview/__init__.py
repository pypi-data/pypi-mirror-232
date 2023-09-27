import requests

class Vectorview:
    def __init__(self, key, project_id=""):
        self.key = key
        self.project_id = project_id

    def event(self, query, docs, query_metadata=None):
        if query_metadata is None:
            query_metadata = {}

        documents = []
        for doc in docs:
            id_ = doc['metadata'].get('id')
            _distance = doc['metadata'].get('_distance')
            content = doc['metadata'].get('content')

            remaining_metadata = {k: v for k, v in doc['metadata'].items() if k not in ['id', '_distance', 'content']}
            
            documents.append([content, id_, _distance, remaining_metadata])

        payload = {
            'miko_key': self.key,
            'project_id': self.project_id,
            'query': query,
            'documents': documents,
            'metadata': query_metadata
        }

        response = requests.post('https://europe-west1-miko-17c4e.cloudfunctions.net/event', json=payload)

        if response.status_code == 200:
            print('Response:', response.json())
        else:
            print('Error:', response.status_code, response.text)
