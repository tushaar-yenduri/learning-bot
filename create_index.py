import requests
import os

SEARCH_ENDPOINT = os.getenv("SEARCH_ENDPOINT")
API_KEY = os.getenv("SEARCH_KEY")

url = f"{SEARCH_ENDPOINT}/indexes/learnix-index?api-version=2023-11-01"

headers = {
    "Content-Type": "application/json",
    "api-key": API_KEY
}

schema = {
    "name": "learnix-index",
    "fields": [
        {"name": "id", "type": "Edm.String", "key": True},
        {"name": "content", "type": "Edm.String", "searchable": True},
        {
            "name": "embedding",
            "type": "Collection(Edm.Single)",
            "searchable": True,
            "dimensions": 1536,
            "vectorSearchProfile": "vector-profile"
        }
    ],
    "vectorSearch": {
        "profiles": [
            {
                "name": "vector-profile",
                "algorithm": "hnsw-config"
            }
        ],
        "algorithms": [
            {
                "name": "hnsw-config",
                "kind": "hnsw"
            }
        ]
    }
}

res = requests.put(url, headers=headers, json=schema)

print(res.status_code)
print(res.text)