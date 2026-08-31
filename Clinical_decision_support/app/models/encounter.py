from typing import Any

from pydantic import BaseModel, Field


class EncounterContext(BaseModel):
    transcript: str = ""
    soap_note: str = ""
    patient_summary: str = ""
    retrieved_guidelines: str = ""
    recommendations: Any = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentMetadata(BaseModel):
    agents_invoked: list[str] = Field(default_factory=list)
