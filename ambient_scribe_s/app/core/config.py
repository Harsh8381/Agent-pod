import os
from dotenv import load_dotenv

load_dotenv()

COFORGE_API_KEY = os.getenv("COFORGE_API_KEY")
print("LOADED KEY =", COFORGE_API_KEY)

COFORGE_ENDPOINT = (
    "https://quasarmarket.coforge.com/qag/llmrouter-api/v2/chat/completions"
)