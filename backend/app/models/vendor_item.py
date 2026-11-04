from sqlalchemy import ForeignKeyConstraint, Integer, Numeric, UniqueConstraint, and_
from sqlalchemy.orm import Mapped, foreign, mapped_column, relationship

from app.db.base import Base
from app.models.inventory import Inventory


class VendorItem(Base):
    __tablename__ = "vendor_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tenant_id: Mapped[int] = mapped_column(Integer, nullable=False)
    vendor_id: Mapped[int] = mapped_column(Integer, nullable=False)
    inventory_id: Mapped[int] = mapped_column(Integer, nullable=False)
    purchase_price: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)

    __table_args__ = (
        UniqueConstraint("tenant_id", "id"),
        UniqueConstraint("tenant_id", "vendor_id", "inventory_id"),
        ForeignKeyConstraint(
            ["tenant_id", "vendor_id"],
            ["vendors.tenant_id", "vendors.id"],
        ),
        ForeignKeyConstraint(
            ["tenant_id", "inventory_id"],
            ["inventory.tenant_id", "inventory.id"],
        ),
        {"mysql_engine": "InnoDB"},
    )

    vendor = relationship("Vendor", back_populates="vendor_items")
    inventory = relationship(
        "Inventory",
        primaryjoin=lambda: and_(
            VendorItem.tenant_id == Inventory.tenant_id,
            foreign(VendorItem.inventory_id) == Inventory.id,
        ),
    )