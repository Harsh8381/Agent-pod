from fastapi import APIRouter

from app.models.schemas import ClinicalNoteRequest
from app.services.llm_service import call_clinical_llm
from app.models.schemas import InsightRequest
from app.services.summary_service import get_detected_insights

router = APIRouter()


@router.post("/generate-note")
async def generate_note(request: ClinicalNoteRequest):

    result = call_clinical_llm(
        request.patient_name,
        request.patient_age,
        request.patient_gender,
        request.doctor_name,
        request.transcript
    )

    return result

@router.post("/insights")
async def detect_insights(
    request: InsightRequest
):

    insights = get_detected_insights(
        request.transcript
    )

    return {
        "insights": insights
    }