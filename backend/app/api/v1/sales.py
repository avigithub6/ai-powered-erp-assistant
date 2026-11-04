from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models import User
from app.repositories.sales_repository import SalesRepository
from app.schemas.sales import (
    SalesOrderDetailResponse,
    SalesOrderListResponse,
)
from app.services.sales_service import SalesService

router = APIRouter(prefix="/sales", tags=["Sales"])


def get_service(db: Session) -> SalesService:
    return SalesService(SalesRepository(db))


@router.get("", response_model=SalesOrderListResponse)
def list_sales(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = get_service(db)
    orders, total = service.list_orders(
        current_user.tenant_id,
        current_user.role,
        limit,
        offset,
        start_date,
        end_date,
    )
    return {
        "items": orders,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/{order_id}", response_model=SalesOrderDetailResponse)
def get_sales(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = get_service(db)
    return service.get_order(
        current_user.tenant_id,
        current_user.role,
        order_id,
    )
