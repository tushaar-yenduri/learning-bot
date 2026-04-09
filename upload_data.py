import json
import requests

SEARCH_ENDPOINT = "https://learnix-search.search.windows.net"
API_KEY = "sI3q6XzavPCe3xbZjUGQ23DzRBmsQHZe3aua70kU9WAzSeAWzSK3"

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