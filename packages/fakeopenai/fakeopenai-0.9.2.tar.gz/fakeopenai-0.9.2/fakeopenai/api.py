import requests

api_key = 'pk-this-is-a-real-free-pool-token-for-everyone'  # Class attribute to hold the API key


class ChatCompletion:
    api_key = api_key  # Class attribute to hold the API key

    @classmethod
    def create(cls, model, messages, functions=None, function_call=None, 
               temperature=None, top_p=None, n=None, stream=None, stop=None, 
               max_tokens=None, presence_penalty=None, frequency_penalty=None, 
               logit_bias=None, user=None):
        
        if cls.api_key is None:
            raise Exception("API key not set. Please set it using ChatCompletion.api_key.")
        
        headers = {
            'Authorization': f'Bearer {cls.api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': model,
            'messages': messages,  # Array of dictionaries with role, content, name, function_call
            'functions': functions,  # Array of dictionaries with name, description, parameters
            'function_call': function_call,
            'temperature': temperature,
            'top_p': top_p,
            'n': n,
            'stream': stream,
            'stop': stop,
            'max_tokens': max_tokens,
            'presence_penalty': presence_penalty,
            'frequency_penalty': frequency_penalty,
            'logit_bias': logit_bias,
            'user': user
        }
        
        # Remove None values from payload
        payload = {k: v for k, v in payload.items() if v is not None}

        response = requests.post('https://ai.fakeopen.com/v1/chat/completions', headers=headers, json=payload)
        if response.status_code != 200:
            raise Exception(f"API call failed with status code {response.status_code}: {response.text}")

        return {'choices': [{'message': response.json()}]}
