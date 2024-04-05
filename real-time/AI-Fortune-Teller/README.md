# realtime-transcription

# 1. Obtain the AssemblyAI API key & OpenAI API

### Store API Keys
Create a folder called `.streamlit` in the project folder. In this folder create a file called `secrets.toml` and paste the below keys in the .toml file:

```python
api_key = 'AssemblyAI-API-KEY'
openai_api_key = 'OpenAI-API-KEY'
```

###  Pip install libraries
```bash
pip install -r requirements.txt
```

###  Launch the app

```bash
streamlit run streamlit_app.py
```
