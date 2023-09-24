import requests
import os

BASE_URL = 'https://ai.fakeopen.com/v1/chat/completions'

class FakeOpenAI:
    api_key = None  # Class attribute to hold the API key

    class ChatCompletion:
        @classmethod
        def create(cls, model, messages, max_tokens=1000):
            if FakeOpenAI.api_key is None:
                raise Exception("API key not set. Please set it using FakeOpenAI.api_key.")
            
            headers = {
                'Authorization': f'Bearer {FakeOpenAI.api_key}',
                'Content-Type': 'application/json'
            }
            payload = {
                'model': model,
                'max_tokens': max_tokens,
                'messages': messages
            }

            response = requests.post(BASE_URL, headers=headers, json=payload)
            if response.status_code != 200:
                raise Exception(f"API call failed with status code {response.status_code}: {response.text}")

            return {'choices': [{'message': response.json()}]}

# # Set API key
# FakeOpenAI.api_key = os.environ.get("FAKEOPENAI_KEY")

# # Usage
# response = FakeOpenAI.ChatCompletion.create(
#     model="gpt-3.5-turbo",
#     messages=[
#         {"role": "system", "content": "You are a helpful assistant."},
#         {"role": "user", "content": "Tell me a joke with 1000 words."},
#     ]
# )

# assistant_reply = response['choices'][0]['message']
# print("Assistant:", assistant_reply)
