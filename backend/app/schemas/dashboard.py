from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class DashboardSummaryResponse(BaseModel):
    total_sales: Decimal | None = None
    total_purchase_value: Decimal | None = None
    sales_order_count: int = 0
    inventory_item_count: int = 0
    low_stock_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class SalesTrendItem(BaseModel):
    month: str
    total_sales: Decimal


class TopProductItem(BaseModel):
    inventory_id: int
    item_name: str
    sku: str
    total_quantity_sold: int


class TopVendorItem(BaseModel):
    vendor_id: int
    vendor_name: str
    total_purchase_value: Decimal


class DashboardInventoryItem(BaseModel):
    id: int
    item_name: str
    sku: str
    stock_level: int
    reorder_level: int
    unit: str


class DashboardInventoryResponse(BaseModel):
    items: list[DashboardInventoryItem]
    total: int
