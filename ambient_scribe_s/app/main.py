from fastapi import FastAPI
from app.api.routes.transcription import router as transcription_router
from app.api.routes.records import router as records_router
from app.api.routes.summary import router as summary_router

app = FastAPI(
    title="AuraMed Clinical Scribe",
    version="1.0.0"
)

app.include_router(
    summary_router,
    prefix="/api/summary",
    tags=["Summary"]
)
app.include_router(
    transcription_router,
    prefix="/api/transcription",
    tags=["Transcription"]
)
app.include_router(
    records_router,
    prefix="/api/records",
    tags=["Records"]
)

@app.get("/")
async def root():
    return {
        "message": "AuraMed Clinical Scribe API Running"
    }