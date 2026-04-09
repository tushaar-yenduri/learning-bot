import json
import os
import requests

SEARCH_ENDPOINT = os.getenv("SEARCH_ENDPOINT")
API_KEY = os.getenv("SEARCH_KEY")

url = f"{SEARCH_ENDPOINT}/indexes/learnix-index/docs/index?api-version=2023-11-01"

headers = {
    "Content-Type": "application/json",
    "api-key": API_KEY
}

with open("embeddings.json", "r") as f:
    data = json.load(f)

docs = []

for i, item in enumerate(data):
    docs.append({
        "@search.action": "upload",
        "id": str(i),
        "content": item["text"],
        "embedding": item["embedding"]
    })

payload = {"value": docs}

res = requests.post(url, headers=headers, json=payload)

print(res.status_code)
print(res.text)