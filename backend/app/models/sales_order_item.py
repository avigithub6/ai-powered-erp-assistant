from sqlalchemy import ForeignKeyConstraint, Integer, Numeric, and_
from sqlalchemy.orm import Mapped, foreign, mapped_column, relationship

from app.db.base import Base
from app.models.inventory import Inventory


class SalesOrderItem(Base):
    __tablename__ = "sales_order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tenant_id: Mapped[int] = mapped_column(Integer, nullable=False)
    sales_order_id: Mapped[int] = mapped_column(Integer, nullable=False)
    inventory_id: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    line_total: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "sales_order_id"],
            ["sales_orders.tenant_id", "sales_orders.id"],
        ),
        ForeignKeyConstraint(
            ["tenant_id", "inventory_id"],
            ["inventory.tenant_id", "inventory.id"],
        ),
        {"mysql_engine": "InnoDB"},
    )

    sales_order = relationship("SalesOrder", back_populates="items")
    inventory = relationship(
        "Inventory",
        primaryjoin=lambda: and_(
            SalesOrderItem.tenant_id == Inventory.tenant_id,
            foreign(SalesOrderItem.inventory_id) == Inventory.id,
        ),
    )