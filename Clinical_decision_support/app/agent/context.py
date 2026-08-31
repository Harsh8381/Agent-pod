from typing import Any

from pydantic import BaseModel, Field


class EncounterContext(BaseModel):
    transcript: str = ""
    soap_note: str = ""
    patient_summary: str = ""
    key_highlights: list[str] = Field(default_factory=list)
    retrieved_guidelines: str = ""
    recommendations: Any = ""
    metadata: dict[str, Any] = Field(default_factory=dict)

    chief_complaint: str = ""
    hpi: str = ""
    past_medical_history: str = ""
    current_medications: str = ""
    assessment: str = ""
    plan: str = ""

    def as_patient_summary(self) -> str:
        return (
            f"Chief Complaint:\n{self.chief_complaint}\n\n"
            f"History of Present Illness:\n{self.hpi}\n\n"
            f"Past Medical History:\n{self.past_medical_history}\n\n"
            f"Current Medications:\n{self.current_medications}\n\n"
            f"Assessment:\n{self.assessment}\n\n"
            f"Plan:\n{self.plan}"
        )


class AgentMetadata(BaseModel):
    agents_invoked: list[str] = Field(default_factory=list)
