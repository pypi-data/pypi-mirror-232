# FakeOpenAI Python Wrapper

A Python wrapper for the FakeOpenAI API, mimicking the functionality provided by the official OpenAI Python package.

## Features

- Send chat completions to the FakeOpenAI API.
- Easy to integrate with existing projects that use the OpenAI Python package.

## Installation

You can install the `fakeopenai` package using pip:

```bash
pip install fakeopenai
```

## Usage

Here's a quick guide to get started with the `fakeopenai` package:

1. **Set your API key**:

```python
import fakeopenai
import os

FAKEOPENAI_KEY = os.environ.get("FAKEOPENAI_KEY")

fakeopenai.set_api_key(FAKEOPENAI_KEY)
```

2. **Generate a response**:

```python
response = fakeopenai.ChatCompletion_create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Tell me a joke."},
    ]
)

assistant_reply = response['choices'][0]['message']['content']
print("Assistant:", assistant_reply)
```

## Documentation

For more detailed information about the methods and functions, refer to the code documentation in the `fakeopenai` directory.

## Contributing

We welcome contributions to this package! If you find any bugs or have suggestions for improvements, please open an issue or submit a pull request.

## License

This package is licensed under the MIT License.

---

Feel free to modify or expand upon this README to better fit your needs or to add any other relevant information about the package.


## Note:

https://github.com/pengzhile/pandora/blob/master/doc/HTTP-API.md
https://github.com/pengzhile/pandora/blob/7aff316c9b4bbc75dc15983a75bef75336b8d0d9/src/pandora/openai/api.py#L314
https://github.com/pengzhile/pandora/issues/837