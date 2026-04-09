import json
from azure.storage.blob import BlobServiceClient
from openai import AzureOpenAI

# -------------------------
# CONFIG
# -------------------------
CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=learnixchunks;AccountKey=c5O2aFPFp1iPt142dllJAA9B1B47pjfE4BC7623AXXvXH+B/6CknmSKSt9Ysjvp4rx6+tlLnDEX6+AStN2SLfg==;EndpointSuffix=core.windows.net"
CONTAINER = "learnix-data"

AZURE_OPENAI_KEY = "3VFNyzILnc5BYbHp41wMDUbr0uXnCiGfX0syAEpjmCT3EJFJnXhbJQQJ99CDACYeBjFXJ3w3AAABACOGfYB2"
AZURE_OPENAI_ENDPOINT = "https://learnix-openai.openai.azure.com/"

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