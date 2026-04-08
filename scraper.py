import requests
from bs4 import BeautifulSoup
import json
from azure.storage.blob import BlobServiceClient
import os
from dotenv import load_dotenv

load_dotenv()

# -------------------------------
# CONFIG
# -------------------------------
BASE_URL = "https://www.w3schools.com"
START_PAGES = [
    "/html/",
    "/css/",
    "/js/",
    "/python/",
    "/sql/",
    "/react/"
]

AZURE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
CONTAINER_NAME = "learnix-data"

# -------------------------------
# HELPER: GET LINKS
# -------------------------------
def get_links(page_url):
    res = requests.get(page_url)
    soup = BeautifulSoup(res.text, "html.parser")

    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]

        if href.startswith("/"):
            full_url = BASE_URL + href
            links.append(full_url)

    return list(set(links))


# -------------------------------
# SCRAPE PAGE CONTENT
# -------------------------------
def scrape_page(url):
    try:
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")

        content = soup.find("div", {"id": "main"})
        if not content:
            return None

        text = content.get_text(separator=" ", strip=True)

        return {
            "url": url,
            "text": text
        }

    except:
        return None


# -------------------------------
# MAIN SCRAPER
# -------------------------------
def scrape():
    all_data = []

    for page in START_PAGES:
        url = BASE_URL + page
        print(f"Scanning: {url}")

        links = get_links(url)

        for link in links[:20]:  # limit for safety
            print(f"Scraping: {link}")

            data = scrape_page(link)
            if data:
                all_data.append(data)

    return all_data


# -------------------------------
# SAVE TO BLOB
# -------------------------------
def upload_to_blob(data):
    blob_service_client = BlobServiceClient.from_connection_string(
        AZURE_CONNECTION_STRING
    )

    blob_client = blob_service_client.get_blob_client(
        container=CONTAINER_NAME,
        blob="raw_data.json"
    )

    json_data = json.dumps(data)

    blob_client.upload_blob(json_data, overwrite=True)
    print("✅ Uploaded raw data to Blob")


# -------------------------------
# RUN
# -------------------------------
if __name__ == "__main__":
    data = scrape()
    print(f"Collected {len(data)} pages")

    upload_to_blob(data)