from google import genai
from pathlib import Path

import os
API_KEY = os.getenv("GEMINI_API_KEY")  # <-- INSERT NEW API KEY HERE

client = genai.Client(api_key=API_KEY)

audio_file = Path("audio.wav")

uploaded_file = client.files.upload(
    file=audio_file
)

response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents=[
        uploaded_file,
        "Transcribe this audio word for word."
    ]
)

print("\n=== TRANSCRIPT ===\n")
print(response.text)

with open("transcript.txt", "w", encoding="utf-8") as f:
    f.write(response.text)

print("\nTranscript saved to transcript.txt")