import json
from typing import Any

from app.agent.cds_agent import ClinicalDecisionSupportAgent


def parse_model_response(raw_response: str) -> dict[str, Any]:
    if not raw_response:
        raise ValueError("Empty response received from LLM.")

    cleaned = raw_response.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.removeprefix("```json").removesuffix("```").strip()

    result = json.loads(cleaned)
    if not isinstance(result, dict):
        raise ValueError("The model response must be a JSON object.")
    return result


class ClinicalAnalysisService:
    def __init__(self, agent: ClinicalDecisionSupportAgent | None = None):
        self.agent = agent or ClinicalDecisionSupportAgent()

    def analyze(self, patient_summary: str) -> tuple[dict[str, Any], str]:
        raw_response = self.agent.analyze(patient_summary.strip())
        return parse_model_response(raw_response), raw_response