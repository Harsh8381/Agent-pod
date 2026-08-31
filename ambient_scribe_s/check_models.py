from google import genai
 
# Replace with your actual API key
import os
API_KEY = os.getenv("GEMINI_API_KEY")  # <-- INSERT NEW API KEY HERE
client = genai.Client(api_key=API_KEY)
 
print("Models available to your API key:")
for model in client.models.list():
    print(model.name)
 