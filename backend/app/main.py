from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import logger
from app.database.database import init_db
from app.api.routes import (
    auth,
    onboarding,
    goals,
    tasks,
    checkins,
    reports,
    dashboard,
    memory,
    chat
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB tables
    logger.info("Initializing Brutality AI database tables...")
    init_db()
    logger.info("Database initialized successfully.")
    yield
    # Shutdown
    logger.info("Brutality AI Backend shutting down.")

app = FastAPI(
    title=settings.APP_NAME,
    description="Backend architecture for BRUTALITY AI: Multi-Agent Accountability System.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
origins = settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if "*" not in origins else ["*"],
    allow_credentials=True if "*" not in origins else False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error. Brutality AI engineers are on it."}
    )

# Health Check
@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
        "ai_provider": settings.AI_PROVIDER,
        "version": "1.0.0"
    }

# Include API Routers under API_V1_PREFIX (/api)
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(onboarding.router, prefix=settings.API_V1_PREFIX)
app.include_router(goals.router, prefix=settings.API_V1_PREFIX)
app.include_router(tasks.router, prefix=settings.API_V1_PREFIX)
app.include_router(checkins.router, prefix=settings.API_V1_PREFIX)
app.include_router(reports.router, prefix=settings.API_V1_PREFIX)
app.include_router(dashboard.router, prefix=settings.API_V1_PREFIX)
app.include_router(memory.router, prefix=settings.API_V1_PREFIX)
app.include_router(chat.router, prefix=settings.API_V1_PREFIX)
