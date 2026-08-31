from fastapi import APIRouter, HTTPException
from datetime import datetime
import uuid

from app.services.storage_service import (
    load_db,
    save_db
)

from app.models.schemas import (
    RecordCreate,
    RecordUpdate
)

router = APIRouter()

@router.get("/")
def get_records():

    return {
        "records": load_db()
    }

@router.get("/{record_id}")
def get_record(record_id: str):

    records = load_db()

    for record in records:
        if record["id"] == record_id:
            return record

    raise HTTPException(
        status_code=404,
        detail="Record not found"
    )

@router.post("/")
def create_record(request: RecordCreate):

    records = load_db()

    new_record = {
        "id": f"PT-{str(uuid.uuid4().int)[:4]}",
        "name": request.name,
        "age": request.age,
        "gender": request.gender,
        "doctor": request.doctor,
        "transcript": request.transcript,
        "summary": request.summary,
        "status": "Pending",
        "date": datetime.now().strftime("%d/%m/%Y"),
        "time": datetime.now().strftime("%H:%M")
    }

    records.insert(0, new_record)

    save_db(records)

    return {
        "message": "Record saved",
        "record": new_record
    }

@router.put("/{record_id}")
def update_record(
    record_id: str,
    request: RecordUpdate
):

    records = load_db()

    for record in records:

        if record["id"] == record_id:

            record["summary"] = request.summary

            save_db(records)

            return {
                "message": "Record updated"
            }

    raise HTTPException(
        status_code=404,
        detail="Record not found"
    )

@router.put("/{record_id}/approve")
def approve_record(record_id: str):

    records = load_db()

    for record in records:

        if record["id"] == record_id:

            record["status"] = "Approved"

            save_db(records)

            return {
                "message": "Record approved"
            }

    raise HTTPException(
        status_code=404,
        detail="Record not found"
    )