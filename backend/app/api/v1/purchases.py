from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models import User
from app.repositories.purchase_repository import PurchaseRepository
from app.schemas.purchase import (
    PurchaseOrderDetailResponse,
    PurchaseOrderListResponse,
)
from app.services.purchase_service import PurchaseService

router = APIRouter(prefix="/purchases", tags=["Purchases"])


def get_service(db: Session) -> PurchaseService:
    return PurchaseService(PurchaseRepository(db))


@router.get("", response_model=PurchaseOrderListResponse)
def list_purchases(
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


@router.get("/{order_id}", response_model=PurchaseOrderDetailResponse)
def get_purchase(
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