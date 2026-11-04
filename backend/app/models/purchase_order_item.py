from sqlalchemy import ForeignKeyConstraint, Integer, Numeric, and_
from sqlalchemy.orm import Mapped, foreign, mapped_column, relationship

from app.db.base import Base
from app.models.inventory import Inventory


class PurchaseOrderItem(Base):
    __tablename__ = "purchase_order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tenant_id: Mapped[int] = mapped_column(Integer, nullable=False)
    purchase_order_id: Mapped[int] = mapped_column(Integer, nullable=False)
    inventory_id: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_cost: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    line_total: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "purchase_order_id"],
            ["purchase_orders.tenant_id", "purchase_orders.id"],
        ),
        ForeignKeyConstraint(
            ["tenant_id", "inventory_id"],
            ["inventory.tenant_id", "inventory.id"],
        ),
        {"mysql_engine": "InnoDB"},
    )

    purchase_order = relationship("PurchaseOrder", back_populates="items")
    inventory = relationship(
        "Inventory",
        primaryjoin=lambda: and_(
            PurchaseOrderItem.tenant_id == Inventory.tenant_id,
            foreign(PurchaseOrderItem.inventory_id) == Inventory.id,
        ),
    )