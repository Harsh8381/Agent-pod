from pydantic import BaseModel
from typing import Optional


class TranscriptRequest(BaseModel):
    transcript: str


class SummaryResponse(BaseModel):
    soap_note: str


class PatientRecord(BaseModel):
    patient_id: str
    patient_name: str
    transcript: str
    soap_note: str
    created_at: str


class AudioUploadResponse(BaseModel):
    transcript: str
    summary: Optional[str] = None

class ClinicalNoteRequest(BaseModel):
    patient_name: str
    patient_age: str
    patient_gender: str
    doctor_name: str
    transcript: str

class RecordCreate(BaseModel):
    name: str
    age: str
    gender: str
    doctor: str
    transcript: str
    summary: str


class RecordUpdate(BaseModel):
    summary: str


class RecordApproval(BaseModel):
    status: str = "Approved"

class InsightRequest(BaseModel):
    transcript: str

