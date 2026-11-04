from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models import User
from app.repositories.dashboard_repository import DashboardRepository
from app.schemas.dashboard import (
    DashboardInventoryResponse,
    DashboardSummaryResponse,
    SalesTrendItem,
    TopProductItem,
    TopVendorItem,
)
from app.services.dashboard_service import DashboardService

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


def get_dashboard_service(db: Session) -> DashboardService:
    return DashboardService(DashboardRepository(db))


@router.get("/summary", response_model=DashboardSummaryResponse)
def get_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = get_dashboard_service(db)
    return service.get_summary(current_user.tenant_id, current_user.role)


@router.get("/sales-trend", response_model=list[SalesTrendItem])
def get_sales_trend(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = get_dashboard_service(db)
    return service.get_sales_trend(current_user.tenant_id, current_user.role)


@router.get("/top-products", response_model=list[TopProductItem])
def get_top_products(
    limit: int = Query(default=5, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = get_dashboard_service(db)
    return service.get_top_products(
        current_user.tenant_id,
        current_user.role,
        limit,
    )


@router.get("/top-vendors", response_model=list[TopVendorItem])
def get_top_vendors(
    limit: int = Query(default=5, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = get_dashboard_service(db)
    return service.get_top_vendors(
        current_user.tenant_id,
        current_user.role,
        limit,
    )


@router.get("/inventory", response_model=DashboardInventoryResponse)
def get_inventory(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = get_dashboard_service(db)
    items, total = service.get_inventory(
        current_user.tenant_id,
        current_user.role,
        limit,
        offset,
    )
    return {"items": items, "total": total}


@router.get("/low-stock", response_model=DashboardInventoryResponse)
def get_low_stock(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = get_dashboard_service(db)
    items, total = service.get_low_stock(
        current_user.tenant_id,
        current_user.role,
        limit,
        offset,
    )
    return {"items": items, "total": total}
