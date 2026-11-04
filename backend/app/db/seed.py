
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from pwdlib import PasswordHash

from app.db.session import SessionLocal
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
    VendorItem,
)

password_hasher = PasswordHash.recommended()
DEMO_PASSWORD = "Demo@12345"


def add_company_data(db, tenant, company_code):
    """Create synthetic ERP records for one tenant."""

    tenant_id = tenant.id

    # Users
    user_data = [
        (f"admin_{company_code}", "Administrator", "Admin"),
        (f"sales_{company_code}", "Sales Executive", "Sales"),
    ]

    if company_code == "a":
        user_data.extend([
            ("purchase_a", "Purchase Executive", "Purchase"),
            ("manager_a", "Management", "Manager"),
        ])

    for username, role, label in user_data:
        db.add(
            User(
                tenant_id=tenant_id,
                username=username,
                full_name=f"{tenant.name} {label}",
                email=f"{username}@example.com",
                password_hash=password_hasher.hash(DEMO_PASSWORD),
                role=role,
                is_active=True,
            )
        )

    # Customers
    customers = [
        Customer(
            tenant_id=tenant_id,
            name=f"{tenant.name} Customer One",
            email=f"customer1_{company_code}@example.com",
            phone="9876543210",
            address="Gurugram, Haryana",
        ),
        Customer(
            tenant_id=tenant_id,
            name=f"{tenant.name} Customer Two",
            email=f"customer2_{company_code}@example.com",
            phone="9876543211",
            address="Delhi, India",
        ),
    ]
    db.add_all(customers)
    db.flush()

    # Inventory: one low-stock item and two normal-stock items
    products = [
        Inventory(
            tenant_id=tenant_id,
            item_name="Mild Steel Sheet",
            sku=f"{company_code.upper()}-STEEL-001",
            category="Steel",
            description="Synthetic mild steel sheet",
            unit="pcs",
            stock_level=5,
            reorder_level=10,
            selling_price=Decimal("2500.00"),
            purchase_price=Decimal("2000.00"),
            is_active=True,
        ),
        Inventory(
            tenant_id=tenant_id,
            item_name="Steel Rod",
            sku=f"{company_code.upper()}-STEEL-002",
            category="Steel",
            description="Synthetic steel rod",
            unit="kg",
            stock_level=100,
            reorder_level=20,
            selling_price=Decimal("120.00"),
            purchase_price=Decimal("95.00"),
            is_active=True,
        ),
        Inventory(
            tenant_id=tenant_id,
            item_name="Industrial Bolt",
            sku=f"{company_code.upper()}-BOLT-001",
            category="Hardware",
            description="Synthetic industrial bolt",
            unit="pcs",
            stock_level=200,
            reorder_level=50,
            selling_price=Decimal("15.00"),
            purchase_price=Decimal("10.00"),
            is_active=True,
        ),
    ]
    db.add_all(products)
    db.flush()

    # Vendors: synthetic Delhi NCR steel suppliers
    vendors = [
        Vendor(
            tenant_id=tenant_id,
            vendor_name=f"{tenant.name} Steel Suppliers",
            contact_person="Rahul Sharma",
            email=f"steel_{company_code}@example.com",
            phone="9810000001",
            address="Industrial Area, Faridabad, Haryana",
        ),
        Vendor(
            tenant_id=tenant_id,
            vendor_name=f"{tenant.name} Industrial Traders",
            contact_person="Amit Verma",
            email=f"traders_{company_code}@example.com",
            phone="9810000002",
            address="Udyog Vihar, Gurugram, Haryana",
        ),
    ]
    db.add_all(vendors)
    db.flush()

    # Vendor-item relationships
    db.add_all([
        VendorItem(
            tenant_id=tenant_id,
            vendor_id=vendors[0].id,
            inventory_id=products[0].id,
            purchase_price=Decimal("2000.00"),
        ),
        VendorItem(
            tenant_id=tenant_id,
            vendor_id=vendors[0].id,
            inventory_id=products[1].id,
            purchase_price=Decimal("95.00"),
        ),
        VendorItem(
            tenant_id=tenant_id,
            vendor_id=vendors[1].id,
            inventory_id=products[2].id,
            purchase_price=Decimal("10.00"),
        ),
    ])

    # Sales orders: one order for each required status
    sales_statuses = ["COMPLETED", "DRAFT", "PENDING", "CANCELLED"]

    for index, status in enumerate(sales_statuses):
        quantity = index + 1
        unit_price = Decimal("2500.00")
        total = unit_price * quantity

        order = SalesOrder(
            tenant_id=tenant_id,
            customer_id=customers[index % len(customers)].id,
            order_number=f"SO-{company_code.upper()}-{index + 1:03d}",
            status=status,
            total_amount=total,
            order_date=datetime.now(UTC) - timedelta(days=30 * index),
        )
        db.add(order)
        db.flush()

        db.add(
            SalesOrderItem(
                tenant_id=tenant_id,
                sales_order_id=order.id,
                inventory_id=products[0].id,
                quantity=quantity,
                unit_price=unit_price,
                line_total=total,
            )
        )

    # Purchase orders: one order for each required status
    purchase_statuses = ["COMPLETED", "DRAFT", "PENDING", "CANCELLED"]

    for index, status in enumerate(purchase_statuses):
        quantity = (index + 1) * 10
        unit_cost = Decimal("2000.00")
        total = unit_cost * quantity

        order = PurchaseOrder(
            tenant_id=tenant_id,
            vendor_id=vendors[index % len(vendors)].id,
            order_number=f"PO-{company_code.upper()}-{index + 1:03d}",
            status=status,
            total_amount=total,
            order_date=datetime.now(UTC) - timedelta(days=20 * index),
        )
        db.add(order)
        db.flush()

        db.add(
            PurchaseOrderItem(
                tenant_id=tenant_id,
                purchase_order_id=order.id,
                inventory_id=products[0].id,
                quantity=quantity,
                unit_cost=unit_cost,
                line_total=total,
            )
        )


def seed_database():
    """Seed both companies atomically; safely prevent duplicate seeding."""

    with SessionLocal.begin() as db:
        existing_a = db.query(Tenant).filter_by(code="COMPANY_A").first()
        existing_b = db.query(Tenant).filter_by(code="COMPANY_B").first()

        if existing_a and existing_b:
            print("Seed data already exists. No changes made.")
            return

        if existing_a or existing_b:
            raise RuntimeError(
                "Partial tenant seed detected. "
                "Please inspect the database before continuing."
            )

        company_a = Tenant(
            name="Company A",
            code="COMPANY_A",
            is_active=True,
        )
        company_b = Tenant(
            name="Company B",
            code="COMPANY_B",
            is_active=True,
        )

        db.add_all([company_a, company_b])
        db.flush()

        add_company_data(db, company_a, "a")
        add_company_data(db, company_b, "b")

    print("Seed data inserted successfully.")
    print("Tenants: 2")
    print("Demo users: 6")
    print("Password for all demo users: Demo@12345")


if __name__ == "__main__":
    seed_database()
