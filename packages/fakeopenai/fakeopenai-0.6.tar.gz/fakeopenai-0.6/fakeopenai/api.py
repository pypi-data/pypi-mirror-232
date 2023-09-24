import requests

# Global variable to hold the API key
api_key = None

class ChatCompletion:
    @classmethod
    def create(cls, model, messages, max_tokens=1000):
        if api_key is None:
            raise Exception("API key not set. Please set it using fakeopenai.api_key.")
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        payload = {
            'model': model,
            'max_tokens': max_tokens,
            'messages': messages
        }

        response = requests.post('https://ai.fakeopen.com/v1/chat/completions', headers=headers, json=payload)
        if response.status_code != 200:
            raise Exception(f"API call failed with status code {response.status_code}: {response.text}")

        return {'choices': [{'message': response.json()}]}
