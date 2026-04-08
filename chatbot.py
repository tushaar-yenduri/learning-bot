import requests
from openai import AzureOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# -----------------------------
# CONFIG
# -----------------------------
SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
SEARCH_KEY = os.getenv("AZURE_SEARCH_API_KEY")
INDEX_NAME = "learnix-index"

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_API_KEY")

EMBEDDING_DEPLOYMENT = "text-embedding-3-small"
CHAT_DEPLOYMENT = "gpt-5.4-mini"

# -----------------------------
# AZURE OPENAI CLIENT
# -----------------------------
client = AzureOpenAI(
    api_key=AZURE_OPENAI_KEY,
    api_version="2024-02-15-preview",
    azure_endpoint=AZURE_OPENAI_ENDPOINT
)

# -----------------------------
# SEARCH FUNCTION
# -----------------------------
def search(query):
    embed = client.embeddings.create(
        model=EMBEDDING_DEPLOYMENT,
        input=query
    ).data[0].embedding

    url = f"{SEARCH_ENDPOINT}/indexes/{INDEX_NAME}/docs/search?api-version=2023-11-01"

    headers = {
        "Content-Type": "application/json",
        "api-key": SEARCH_KEY
    }

    payload = {
        "vectorQueries": [
            {
                "vector": embed,
                "k": 5,
                "fields": "embedding"
            }
        ]
    }

    res = requests.post(url, headers=headers, json=payload)
    results = res.json()

    return [doc["content"] for doc in results.get("value", [])]
# -----------------------------
# ASK FUNCTION
# -----------------------------
def ask(question):
    docs = search(question)

    context = "\n\n".join(docs)

    response = client.chat.completions.create(
        model=CHAT_DEPLOYMENT,
        messages=[
            {"role": "system", "content": "Answer using only the given context."},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion:\n{question}"}
        ]
    )

    return response.choices[0].message.content

# -----------------------------
# RUN LOOP
# -----------------------------
if __name__ == "__main__":
    while True:
        q = input("Ask: ")
        print(ask(q))