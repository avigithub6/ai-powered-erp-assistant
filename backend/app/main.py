from fastapi import FastAPI

from app.api.v1.ai import router as ai_router
from app.api.v1.auth import router as auth_router
from app.api.v1.customers import router as customers_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.inventory import router as inventory_router
from app.api.v1.purchases import router as purchases_router
from app.api.v1.sales import router as sales_router
from app.api.v1.vendors import router as vendors_router
from app.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    description="Multi-Tenant AI-Powered ERP Assistant API",
)

routers = [
    auth_router,
    dashboard_router,
    sales_router,
    purchases_router,
    inventory_router,
    vendors_router,
    customers_router,
    ai_router,
]

for router in routers:
    app.include_router(router, prefix=settings.API_V1_PREFIX)


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
