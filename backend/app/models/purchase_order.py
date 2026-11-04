from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKeyConstraint,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tenant_id: Mapped[int] = mapped_column(Integer, nullable=False)
    vendor_id: Mapped[int] = mapped_column(Integer, nullable=False)
    order_number: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="DRAFT")
    total_amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False, default=0)
    order_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("tenant_id", "id"),
        UniqueConstraint("tenant_id", "order_number"),
        ForeignKeyConstraint(
            ["tenant_id", "vendor_id"],
            ["vendors.tenant_id", "vendors.id"],
        ),
        Index("ix_purchase_orders_tenant_status", "tenant_id", "status"),
        {"mysql_engine": "InnoDB"},
    )

    vendor = relationship("Vendor")
    items = relationship("PurchaseOrderItem", back_populates="purchase_order")
