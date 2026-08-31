from fastapi import APIRouter, UploadFile, File

from app.services.transcription_service import transcribe_audio

router = APIRouter()


@router.post("/upload")
async def upload_audio(
    file: UploadFile = File(...)
):

    audio_bytes = await file.read()

    transcript = transcribe_audio(audio_bytes)

    return {
        "transcript": transcript
    }