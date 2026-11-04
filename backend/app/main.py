from fastapi import FastAPI

from app.api.v1.auth import router as auth_router
from app.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    description="Multi-Tenant AI-Powered ERP Assistant API",
)


app.include_router(
    auth_router,
    prefix=settings.API_V1_PREFIX,
)


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Welcome to AI-Powered ERP Assistant",
        "docs": "/docs",
        "health": "/health",
    }