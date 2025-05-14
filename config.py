import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "customer_support")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "payments")

# Gemini Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

# Chroma Configuration
CHROMA_PERSIST_DIRECTORY = os.getenv("CHROMA_PERSIST_DIRECTORY", "chroma_db")
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "conversation_memory")

# Support Agent Configuration
MAX_MEMORY_ITEMS = int(os.getenv("MAX_MEMORY_ITEMS", "10"))
SYSTEM_PROMPT = """You are a helpful customer support agent for an e-commerce store. 
You can look up customer purchase information when they provide their purchase ID.
Be friendly, professional, and concise in your responses.
If you don't know something, say so clearly and ask for more information if needed."""