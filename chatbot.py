import requests
import os
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

# -----------------------------
# CONFIG
# -----------------------------
SEARCH_ENDPOINT = os.getenv("SEARCH_ENDPOINT")
SEARCH_KEY = os.getenv("SEARCH_KEY")
INDEX_NAME = "learnix-index"

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")

EMBEDDING_DEPLOYMENT = "text-embedding-3-small"
CHAT_DEPLOYMENT = "gpt-5.4-mini"

# Unsafe keywords to block
UNSAFE_KEYWORDS = [
    # Violence & harm
    "hack", "exploit", "bypass", "sql injection",
    "bomb", "kill", "terror", "violence", "attack",
    "harm", "hurt", "injure", "murder", "suicide",
    "self harm", "cut", "poison", "overdose",
    # Hate & discrimination
    "hate", "racist", "sexist", "discriminate",
    # Sexual content
    "porn", "sexual", "nude", "xxx"
]

# Allowed topics for web development domain
ALLOWED_TOPICS = [
    "html", "css", "javascript", "js", "python",
    "sql", "react", "web development", "coding",
    "programming", "frontend", "backend", "database",
    "api", "rest", "http", "node", "express"
]

# -----------------------------
# AZURE OPENAI CLIENT
# -----------------------------
client = AzureOpenAI(
    api_key=AZURE_OPENAI_KEY,
    api_version="2024-02-15-preview",
    azure_endpoint=AZURE_OPENAI_ENDPOINT
)

# -----------------------------
# PHASE 4 GUARDRAILS
# -----------------------------

def is_safe_query(query):
    """
    Check if query is safe and doesn't contain harmful content.
    
    Args:
        query (str): User input query
        
    Returns:
        bool: True if safe, False if unsafe
    """
    query_lower = query.lower()
    for keyword in UNSAFE_KEYWORDS:
        if keyword in query_lower:
            return False
    return True


def is_relevant_query(query):
    """
    Check if query is relevant to web development topics.
    
    Args:
        query (str): User input query
        
    Returns:
        bool: True if relevant, False if irrelevant
    """
    query_lower = query.lower()
    for topic in ALLOWED_TOPICS:
        if topic in query_lower:
            return True
    return False

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
# ASK FUNCTION (Enhanced with guardrails)
# -----------------------------
def ask(question):
    """
    Answer user question using RAG with Azure OpenAI and Search.
    Uses strengthened system prompt with production guardrails.
    
    Args:
        question (str): User question
        
    Returns:
        str: Chatbot response
    """
    try:
        docs = search(question)

        context = "\n\n".join(docs)

        # Strengthened system prompt with production guardrails
        system_prompt = """You are Learnix AI, a web development tutor.

Rules:
- Answer only using the provided context.
- If the answer is not in context, say: 'I don't have enough information.'
- Do not hallucinate.
- Do not make up answers.
- Stay within coding and web development topics.
- Be helpful, clear, and concise."""

        response = client.chat.completions.create(
            model=CHAT_DEPLOYMENT,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion:\n{question}"}
            ]
        )

        return response.choices[0].message.content
    
    except Exception as e:
        # Handle Azure content filter and other errors gracefully
        error_str = str(e).lower()
        if "content_filter" in error_str or "content management policy" in error_str:
            return "⚠️ This query violates content policies. Please rephrase."
        else:
            return f"⚠️ Error: {str(e)[:100]}"

# -----------------------------
# MAIN INPUT LOOP (with Phase 4 Guardrails)
# -----------------------------
if __name__ == "__main__":
    print("🤖 Learnix AI Chat - Web Development Tutor")
    print("Type 'exit' to quit.\n")
    
    while True:
        q = input("Ask: ").strip()
        
        # Exit command
        if q.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break
        
        # Skip empty input
        if not q:
            continue
        
        # Phase 4 Guardrail 1: Safety filter
        if not is_safe_query(q):
            print("⚠️ Unsafe query blocked.\n")
            continue
        
        # Phase 4 Guardrail 2: Domain restriction
        if not is_relevant_query(q):
            print("⚠️ I can only help with web development topics.\n")
            continue
        
        # All guardrails passed - process question
        print(ask(q))
        print()