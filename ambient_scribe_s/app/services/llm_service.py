import requests

from app.core.config import (
    COFORGE_API_KEY,
    COFORGE_ENDPOINT
)


def call_clinical_llm(
    pat_name,
    pat_age,
    pat_gender,
    doctor_str,
    transcript
):
    system_prompt = f"""
You are an expert physician assistant. You will receive a raw, unpunctuated voice transcript.

TASK 1: STRICT DIARIZATION (NO HALLUCINATIONS)

Reconstruct the raw transcript into a readable dialogue.

CRITICAL RULES:
1. DO NOT invent, hallucinate, or add automated questions.
2. Only use the exact words provided.
3. Label dialogue as "{doctor_str}:" or "Patient ({pat_name}):"

Start exactly with "--- DIARIZED TRANSCRIPT ---".

TASK 2: CLINICAL NOTE

Generate a strict medical note.

Start exactly with:

--- CLINICAL NOTE ---
"""

    try:

        headers = {
            "Content-Type": "application/json",
            "X-API-KEY": COFORGE_API_KEY
        }

        body = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": f"""
Patient: {pat_name}
Age: {pat_age}
Gender: {pat_gender}

Transcript:
{transcript}
"""
                }
            ],
            "temperature": 0.2
        }

        print("\n" + "=" * 60)
        print("COFORGE API DEBUG")
        print("=" * 60)
        print("API KEY:", COFORGE_API_KEY)
        print("ENDPOINT:", COFORGE_ENDPOINT)
        print("HEADERS:", headers)
        print("=" * 60)

        resp = requests.post(
            COFORGE_ENDPOINT,
            headers=headers,
            json=body,
            timeout=40
        )

        print("\nSTATUS CODE:", resp.status_code)
        print("RESPONSE BODY:")
        print(resp.text)
        print("=" * 60 + "\n")

        diarized_transcript = ""
        summary = ""

        if resp.status_code == 200:

            data = resp.json()

            response_text = data["choices"][0]["message"]["content"]

            if "--- CLINICAL NOTE ---" in response_text:

                parts = response_text.split(
                    "--- CLINICAL NOTE ---"
                )

                diarized_transcript = (
                    parts[0]
                    .replace(
                        "--- DIARIZED TRANSCRIPT ---",
                        ""
                    )
                    .strip()
                )

                summary = parts[1].strip()

            else:
                diarized_transcript = transcript
                summary = response_text

        else:

            diarized_transcript = transcript
            summary = f"API Error: {resp.status_code}"

        return {
            "transcript": diarized_transcript,
            "summary": summary
        }

    except Exception as e:
        import traceback

    print("\n===== EXCEPTION =====")
    traceback.print_exc()
    print("=====================\n")

    return {
        "transcript": transcript,
        "summary": f"Request failed: {str(e)}"
    }
