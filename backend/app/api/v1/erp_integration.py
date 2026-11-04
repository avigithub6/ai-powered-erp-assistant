
import logging
from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict

from app.core.permissions import require_permission
from app.integrations.spring_boot_client import SpringBootERPClient
from app.models import User

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/erp-integration",
    tags=["ERP Integration"],
)


class IntegratedSalesOrder(BaseModel):
    id: int
    order_number: str
    status: str
    total_amount: Decimal
    order_date: datetime

    model_config = ConfigDict(extra="forbid")


class IntegratedSalesOrderList(BaseModel):
    items: list[IntegratedSalesOrder]
    total: int
    limit: int
    offset: int


@router.get(
    "/sales/orders",
    response_model=IntegratedSalesOrderList,
)
async def get_integrated_sales_orders(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(require_permission("sales:read")),
):
    client = SpringBootERPClient()

    try:
        result = await client.get_sales_orders(
            tenant_id=current_user.tenant_id,
            limit=limit,
            offset=offset,
        )

        return IntegratedSalesOrderList.model_validate(result)

    except RuntimeError as exc:
        logger.error(
            "ERP integration failed for tenant_id=%s",
            current_user.tenant_id,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ERP integration service is currently unavailable",
        ) from exc

    except Exception as exc:
        logger.exception(
            "Unexpected ERP integration error for tenant_id=%s",
            current_user.tenant_id,
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Invalid response from ERP integration service",
        ) from exc
