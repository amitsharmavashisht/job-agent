import os
from dotenv import load_dotenv

load_dotenv()

# ═══════════════════════════════════════════════
# 1. API KEYS
# ═══════════════════════════════════════════════
SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")

# ═══════════════════════════════════════════════
# 2. TELEGRAM (For Alerts)
# ═══════════════════════════════════════════════
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# ═══════════════════════════════════════════════
# 3. EMAIL SETTINGS
# ═══════════════════════════════════════════════
EMAIL_SENDER = os.getenv("EMAIL_SENDER", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER", "")

# ═══════════════════════════════════════════════
# 4. SEARCH SETTINGS (Tailored for Amit Sharma)
# ═══════════════════════════════════════════════
SEARCH_QUERIES = [
    "AI Engineer intern",
    "Generative AI fresher",
    "LLM developer junior",
    "Machine Learning Engineer intern",
    "AI Automation Engineer",
    "Data Engineer fresher",
    "Python Developer AI",
]

LOCATION = "India"
DATE_POSTED = "week"
RESULTS_PER_Q = 10

# ═══════════════════════════════════════════════
# 5. YOUR RESUME SKILLS (For Matching)
# ═══════════════════════════════════════════════
MY_RESUME_SKILLS = [
    "python", "langchain", "langgraph", "rag", "llm",
    "fastapi", "flask", "docker", "sql", "pytorch",
    "tensorflow", "nlp", "automation", "n8n", "pandas",
    "numpy", "git", "aws", "linux", "chromadb", "faiss",
    "openai api", "gemini", "hugging face", "rest api"
]

MY_STRONG_SKILLS = [
    "langchain", "rag", "llm", "generative ai", 
    "fastapi", "n8n", "python", "automation"
]

# ═══════════════════════════════════════════════
# 6. KEYWORDS FOR FILTERING
# ═══════════════════════════════════════════════
FRESHER_KEYWORDS = [
    "fresher", "intern", "internship", "trainee", 
    "entry level", "entry-level", "graduate", 
    "junior", "associate", "0-1 years", "6 months"
]

SENIOR_KEYWORDS = [
    "senior", "lead", "principal", "architect", 
    "manager", "head of", "director", "cto",
    "5 years", "7 years", "10 years", "8+ years"
]