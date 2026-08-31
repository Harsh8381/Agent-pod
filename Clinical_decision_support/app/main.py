from fastapi import FastAPI

from app.api.routes import router


def create_app() -> FastAPI:
    application = FastAPI(
        title="Clinical Decision Support API",
        description="Decision-support suggestions grounded in the local medical knowledge base.",
        version="1.0.0",
    )
    application.include_router(router)
    return application


app = create_app()