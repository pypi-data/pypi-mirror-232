from setuptools import setup, find_packages

setup(
    name="fakeopenai",
    version="0.8",
    description="A Fake OpenAI API based on pandora",
    packages=find_packages(),
    install_requires=[
        "requests",
    ],
)
