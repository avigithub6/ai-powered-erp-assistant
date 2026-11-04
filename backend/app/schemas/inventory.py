from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class SalesInventoryResponse(BaseModel):
    id: int
    item_name: str
    sku: str
    category: str | None
    stock_level: int
    reorder_level: int
    selling_price: Decimal
    unit: str

    model_config = ConfigDict(from_attributes=True)


class ProcurementInventoryResponse(SalesInventoryResponse):
    purchase_price: Decimal


class InventoryListResponse(BaseModel):
    items: list[SalesInventoryResponse | ProcurementInventoryResponse]
    total: int
    limit: int
    offset: int
