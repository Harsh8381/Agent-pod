import json
from typing import Any

from app.llm_client import call_llm


class SoapService:
    def generate(self, transcript: str) -> dict[str, Any]:
        response = call_llm(
            prompt=(
                "Convert the following clinical conversation into a structured clinical note. "
                "Return only valid JSON with exactly these string fields: "
                '{"soap_note":"", "patient_summary":""}\n\n'
                f"Transcript:\n{transcript}"
            ),
            system_prompt=(
                "You are an ambient clinical scribe. Extract only information stated in the transcript. "
                "Do not invent diagnoses, medications, or treatment decisions. Return JSON only."
            ),
            temperature=0.2,
        )
        return self._parse_response(response)

    @staticmethod
    def _parse_response(response: str) -> dict[str, Any]:
        cleaned = response.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.removeprefix("```json").removesuffix("```").strip()

        data = json.loads(cleaned)
        if not isinstance(data, dict):
            raise ValueError("Scribe response must be a JSON object.")
        return data