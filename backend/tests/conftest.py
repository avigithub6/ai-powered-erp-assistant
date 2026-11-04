import pytest
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import (
    Customer,
    Inventory,
    PurchaseOrder,
    PurchaseOrderItem,
    SalesOrder,
    SalesOrderItem,
    Tenant,
    User,
    Vendor,
)
from app.security.password import get_password_hash
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(bind=engine)

    with Session(engine) as db:
        company_a = Tenant(
            id=1,
            name="Company A",
            code="COMPANY_A",
            is_active=True,
        )
        company_b = Tenant(
            id=2,
            name="Company B",
            code="COMPANY_B",
            is_active=True,
        )

        db.add_all([company_a, company_b])
        db.flush()

        password_hash = get_password_hash("Demo@12345")

        users = [
            User(
                id=1,
                tenant_id=1,
                username="admin_a",
                full_name="Company A Admin",
                email="admin_a@example.com",
                password_hash=password_hash,
                role="Administrator",
                is_active=True,
            ),
            User(
                id=2,
                tenant_id=1,
                username="sales_a",
                full_name="Company A Sales",
                email="sales_a@example.com",
                password_hash=password_hash,
                role="Sales Executive",
                is_active=True,
            ),
            User(
                id=3,
                tenant_id=2,
                username="admin_b",
                full_name="Company B Admin",
                email="admin_b@example.com",
                password_hash=password_hash,
                role="Administrator",
                is_active=True,
            ),
            User(
                id=4,
                tenant_id=1,
                username="purchase_a",
                full_name="Company A Purchase",
                email="purchase_a@example.com",
                password_hash=password_hash,
                role="Purchase Executive",
                is_active=True,
            ),
            User(
                id=5,
                tenant_id=1,
                username="manager_a",
                full_name="Company A Manager",
                email="manager_a@example.com",
                password_hash=password_hash,
                role="Management",
                is_active=True,
            ),
        ]

        db.add_all(users)
        db.flush()

        for tenant_id, suffix in [(1, "A"), (2, "B")]:
            customer = Customer(
                tenant_id=tenant_id,
                name=f"Customer {suffix}",
                email=f"customer_{suffix.lower()}@example.com",
            )
            vendor = Vendor(
                tenant_id=tenant_id,
                vendor_name=f"Vendor {suffix}",
                contact_person=f"Contact {suffix}",
                email=f"vendor_{suffix.lower()}@example.com",
            )
            inventory = Inventory(
                tenant_id=tenant_id,
                item_name=f"Product {suffix}",
                sku=f"SKU-{suffix}",
                category="Electronics",
                unit="pcs",
                stock_level=5,
                reorder_level=10,
                selling_price=100,
                purchase_price=60,
                is_active=True,
            )

            db.add_all([customer, vendor, inventory])
            db.flush()

            sales_order = SalesOrder(
                tenant_id=tenant_id,
                customer_id=customer.id,
                order_number=f"SO-{suffix}-001",
                status="COMPLETED",
                total_amount=200,
            )
            purchase_order = PurchaseOrder(
                tenant_id=tenant_id,
                vendor_id=vendor.id,
                order_number=f"PO-{suffix}-001",
                status="COMPLETED",
                total_amount=120,
            )

            db.add_all([sales_order, purchase_order])
            db.flush()

            db.add_all([
                SalesOrderItem(
                    tenant_id=tenant_id,
                    sales_order_id=sales_order.id,
                    inventory_id=inventory.id,
                    quantity=2,
                    unit_price=100,
                    line_total=200,
                ),
                PurchaseOrderItem(
                    tenant_id=tenant_id,
                    purchase_order_id=purchase_order.id,
                    inventory_id=inventory.id,
                    quantity=2,
                    unit_cost=60,
                    line_total=120,
                ),
            ])

        db.commit()

        yield db

    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
