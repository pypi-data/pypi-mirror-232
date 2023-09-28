import requests

class Vectorview:
    def __init__(self, key, project_id="default"):
        self.key = key
        self.project_id = project_id

    def _convert_to_string(self, o):
        """Convert all values in an object to strings."""
        if isinstance(o, list):
            return [self._convert_to_string(item) for item in o]
        if isinstance(o, dict):
            return {k: self._convert_to_string(v) for k, v in o.items()}
        return str(o)

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
            'sender': 'py',
            'vv_key': self.key,
            'project_id': self.project_id,
            'query': query,
            'documents': documents,
            'metadata': query_metadata
        }
        payload = self._convert_to_string(payload)

        print("Payload", payload)

        response = requests.post('https://europe-west1-miko-17c4e.cloudfunctions.net/event', json=payload)
        print("Response", response)

        return response
