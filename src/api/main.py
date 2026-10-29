from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.settings import settings
from src.api.routes.health import router as health_router
from src.api.routes.research import router as research_router
from src.api.routes.properties import router as properties_router
from src.api.routes.financial import router as financial_router

def create_app() -> FastAPI:
    app = FastAPI(
        title="Atlas AQAR API",
        description="Agentic AI-Driven Real-Estate Research and Investment Intelligence System",
        version=settings.VERSION,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include Routers
    app.include_router(health_router, prefix="/api/v1")
    app.include_router(research_router, prefix="/api/v1")
    app.include_router(properties_router, prefix="/api/v1")
    app.include_router(financial_router, prefix="/api/v1")

    return app

app = create_app()
