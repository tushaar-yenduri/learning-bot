import json
from azure.storage.blob import BlobServiceClient
from openai import AzureOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# -------------------------
# CONFIG
# -------------------------
CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
CONTAINER = "learnix-data"

AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")

EMBEDDING_MODEL = "text-embedding-3-small"

# -------------------------
# CLIENTS
# -------------------------
blob_service = BlobServiceClient.from_connection_string(CONNECTION_STRING)

client = AzureOpenAI(
    api_key=AZURE_OPENAI_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_version="2024-02-01"
)

# -------------------------
# LOAD CHUNKS
# -------------------------
blob_client = blob_service.get_blob_client(CONTAINER, "chunks.json")
data = json.loads(blob_client.download_blob().readall())

print(f"Loaded {len(data)} chunks")

# -------------------------
# GENERATE EMBEDDINGS
# -------------------------
results = []

for i, item in enumerate(data[:50]):  # start small
    try:
        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=item["text"]
        )

        embedding = response.data[0].embedding

        results.append({
            "text": item["text"],
            "embedding": embedding
        })

        print(f"✅ {i+1} done")

    except Exception as e:
        print(f"❌ Error at {i}: {e}")

# -------------------------
# SAVE LOCALLY
# -------------------------
with open("embeddings.json", "w") as f:
    json.dump(results, f)

print("🎉 Embeddings saved!")