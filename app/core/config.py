import os
from dotenv import load_dotenv

load_dotenv()

SOURCE = "https://raw.githubusercontent.com/tnahddisttud/sample-doc/refs/heads/main/AtliqAI_HR_Policies.pdf"

EMBED_MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"

QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "hr_docs"

GROQ_MODEL = "openai/gpt-oss-20b"

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
