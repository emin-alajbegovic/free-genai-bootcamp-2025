from setuptools import setup, find_packages

setup(
    name="listening-comp",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'streamlit',
        'boto3',
        'google-cloud-texttospeech',
        'azure-cognitiveservices-speech'
    ]
) 