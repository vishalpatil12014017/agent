import os
from dotenv import load_dotenv
# 1. Load the .env file first so os.getenv doesn't return None!
load_dotenv()
#llm model used
LLM_MODEL="gemini/gemini-3.5-flash-lite"
#api key
GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")
print(f"Gemini API Key: {GEMINI_API_KEY}")