import json
from azure.storage.blob import BlobServiceClient

# CONFIG
CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=learnixchunks;AccountKey=c5O2aFPFp1iPt142dllJAA9B1B47pjfE4BC7623AXXvXH+B/6CknmSKSt9Ysjvp4rx6+tlLnDEX6+AStN2SLfg==;EndpointSuffix=core.windows.net"
CONTAINER = "learnix-data"

CHUNK_SIZE = 500
OVERLAP = 50


def clean_text(text):
    return " ".join(text.split())


def chunk_text(text):
    words = text.split()
    chunks = []

    i = 0
    while i < len(words):
        chunk = words[i:i + CHUNK_SIZE]
        chunks.append(" ".join(chunk))
        i += CHUNK_SIZE - OVERLAP

    return chunks


def main():
    blob_service = BlobServiceClient.from_connection_string(CONNECTION_STRING)

    # Download raw data
    blob_client = blob_service.get_blob_client(CONTAINER, "raw_data.json")
    data = json.loads(blob_client.download_blob().readall())

    all_chunks = []

    for item in data:
        cleaned = clean_text(item["text"])
        chunks = chunk_text(cleaned)

        for chunk in chunks:
            all_chunks.append({
                "text": chunk,
                "source": item["url"]
            })

    print(f"Total chunks: {len(all_chunks)}")

    # Upload chunks
    blob_client = blob_service.get_blob_client(CONTAINER, "chunks.json")
    blob_client.upload_blob(json.dumps(all_chunks), overwrite=True)

    print("✅ Chunks uploaded")


if __name__ == "__main__":
    main()