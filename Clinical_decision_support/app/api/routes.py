from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from pydantic import ValidationError

from app.api.schemas import (
    EncounterRequest,
    EncounterContextRequest,
    EncounterResponse,
    KnowledgeBaseRequest,
    KnowledgeBaseResponse,
    PatientAnalysisRequest,
    PatientAnalysisResponse,
)
from app.agent.encounter_agent import EncounterAgent
from app.services.clinical_service import ClinicalAnalysisService


router = APIRouter()


def get_encounter_agent() -> EncounterAgent:
    return EncounterAgent()


def get_transcription_service() -> TranscriptionService:
    from app.services.transcription_service import TranscriptionService

    return TranscriptionService()


def retrieve_documents(query: str, top_k: int) -> str:
    from app.rag.retriever import retrieve_documents as retrieve

    return retrieve(query, top_k)


@router.get("/", tags=["system"])
def root():
    return {"name": "Clinical Decision Support API", "docs": "/docs", "health": "/health"}


@router.get("/health", tags=["system"])
def health_check():
    return {"status": "ok"}


@router.post("/analyze", response_model=PatientAnalysisResponse, tags=["clinical"])
def analyze_patient(request: PatientAnalysisRequest):
    try:
        result, raw_response = ClinicalAnalysisService().analyze(request.patient_summary)
    except ValueError as error:
        raise HTTPException(status_code=502, detail="The model response was not valid JSON.") from error
    except FileNotFoundError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"Clinical analysis failed: {error}") from error

    response_fields = {
        "possible_diagnosis",
        "risk_assessment",
        "recommended_tests",
        "treatment_suggestions",
        "follow_up_plan",
    }
    try:
        return PatientAnalysisResponse(
            raw_response=raw_response,
            **{key: result[key] for key in response_fields if key in result},
        )
    except ValidationError as error:
        raise HTTPException(status_code=502, detail="The model response had an invalid structure.") from error


@router.post("/encounters/analyze", response_model=EncounterResponse, tags=["encounters"])
def analyze_encounter(request: EncounterRequest):
    try:
        agent = get_encounter_agent()
        if request.include_cds and hasattr(agent, "process"):
            context = agent.process(request.transcript.strip())
        else:
            context = agent.prepare(request.transcript.strip())
            if request.include_cds:
                context = agent.add_clinical_decision_support(context)
    except ValueError as error:
        raise HTTPException(status_code=502, detail=f"Ambient scribe response was invalid: {error}") from error
    except FileNotFoundError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except ConnectionError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"Encounter analysis failed: {error}") from error

    return EncounterResponse(**context.model_dump())


@router.post("/encounters/scribe", response_model=EncounterResponse, tags=["encounters"])
def scribe_encounter(request: EncounterRequest):
    try:
        context = get_encounter_agent().prepare(request.transcript.strip())
    except ValueError as error:
        raise HTTPException(status_code=502, detail=f"Ambient scribe response was invalid: {error}") from error
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"Scribe analysis failed: {error}") from error

    return EncounterResponse(**context.model_dump())


@router.post("/encounters/cds", response_model=EncounterResponse, tags=["encounters"])
def complete_encounter_with_cds(request: EncounterContextRequest):
    try:
        context = get_encounter_agent().add_clinical_decision_support(request)
    except FileNotFoundError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except ConnectionError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"CDS analysis failed: {error}") from error

    return EncounterResponse(**context.model_dump())


@router.post("/encounters/analyze-audio", response_model=EncounterResponse, tags=["encounters"])
async def analyze_audio(request: Request):
    try:
        form = await request.form()
        file = form.get("file")
        if file is None or not hasattr(file, "read"):
            raise ValueError("An audio file is required.")
        transcript = get_transcription_service().transcribe(await file.read())
        context = get_encounter_agent().process(transcript.strip())
    except ValueError as error:
        raise HTTPException(status_code=502, detail=f"Encounter processing failed: {error}") from error
    except FileNotFoundError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"Audio encounter analysis failed: {error}") from error

    return EncounterResponse(**context.model_dump())


@router.post("/retrieve", response_model=KnowledgeBaseResponse, tags=["knowledge base"])
def retrieve_knowledge(request: KnowledgeBaseRequest):
    try:
        context = retrieve_documents(request.query.strip(), top_k=request.top_k)
    except FileNotFoundError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Knowledge-base retrieval failed: {error}") from error

    return KnowledgeBaseResponse(query=request.query, top_k=request.top_k, context=context)