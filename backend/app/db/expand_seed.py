from datetime import UTC, datetime, timedelta
from decimal import Decimal

from app.db.session import SessionLocal
from app.models import (
    Customer,
    Inventory,
    PurchaseOrder,
    PurchaseOrderItem,
    SalesOrder,
    SalesOrderItem,
    Tenant,
    Vendor,
    VendorItem,
)

PRODUCTS_A = [
    ("Aluminium Sheet", "ALUMINIUM", "Metal", "kg", 180, 130),
    ("Copper Wire", "COPPER", "Electrical", "kg", 750, 620),
    ("GI Pipe", "PIPE", "Steel", "pcs", 950, 780),
    ("Safety Helmet", "HELMET", "Safety", "pcs", 450, 320),
    ("Welding Machine", "WELD", "Equipment", "pcs", 12500, 9800),
    ("Industrial Paint", "PAINT", "Chemical", "ltr", 280, 210),
    ("PVC Cable", "CABLE", "Electrical", "mtr", 85, 60),
    ("Bearing 6205", "BEARING", "Mechanical", "pcs", 320, 240),
    ("Steel Plate", "PLATE", "Steel", "kg", 110, 88),
    ("Hydraulic Pump", "PUMP", "Equipment", "pcs", 8500, 6900),
    ("Rubber Gasket", "GASKET", "Hardware", "pcs", 45, 30),
    ("Power Drill", "DRILL", "Equipment", "pcs", 3200, 2500),
]

PRODUCTS_B = [
    ("Stainless Steel Coil", "SSCOIL", "Steel", "kg", 220, 175),
    ("Brass Connector", "BRASS", "Hardware", "pcs", 160, 115),
    ("LED Panel", "LED", "Electrical", "pcs", 1250, 920),
    ("Fire Extinguisher", "FIRE", "Safety", "pcs", 1800, 1400),
    ("Air Compressor", "COMPRESSOR", "Equipment", "pcs", 18000, 14500),
    ("Industrial Lubricant", "LUBRICANT", "Chemical", "ltr", 390, 290),
    ("Control Cable", "CONTROL", "Electrical", "mtr", 125, 90),
    ("Roller Bearing", "ROLLER", "Mechanical", "pcs", 560, 410),
    ("MS Channel", "CHANNEL", "Steel", "kg", 95, 72),
    ("Gear Motor", "GEARMOTOR", "Equipment", "pcs", 14500, 11500),
    ("Nylon Washer", "WASHER", "Hardware", "pcs", 12, 8),
    ("Angle Grinder", "GRINDER", "Equipment", "pcs", 2800, 2150),
]


def get_or_create_products(db, tenant_id, company_code):
    definitions = PRODUCTS_A if company_code == "A" else PRODUCTS_B

    for index, item in enumerate(definitions, start=1):
        name, sku, category, unit, selling, purchase = item
        full_sku = f"{company_code}-EXP-{sku}"

        product = db.query(Inventory).filter_by(
            tenant_id=tenant_id,
            sku=full_sku,
        ).first()

        if product is None:
            product = Inventory(
                tenant_id=tenant_id,
                item_name=name,
                sku=full_sku,
                category=category,
                description=f"Synthetic demo product {name}",
                unit=unit,
                stock_level=5 if index % 4 == 0 else 100 + index * 10,
                reorder_level=15 if index % 4 == 0 else 20,
                selling_price=Decimal(str(selling)),
                purchase_price=Decimal(str(purchase)),
                is_active=True,
            )
            db.add(product)

    db.flush()

    return (
        db.query(Inventory)
        .filter_by(tenant_id=tenant_id, is_active=True)
        .order_by(Inventory.id)
        .all()
    )


def get_or_create_customers(db, tenant_id, company_code):
    for index in range(1, 11):
        email = f"customer{index}_{company_code.lower()}@demo.example.com"

        customer = db.query(Customer).filter_by(
            tenant_id=tenant_id,
            email=email,
        ).first()

        if customer is None:
            db.add(
                Customer(
                    tenant_id=tenant_id,
                    name=f"Company {company_code} Customer {index}",
                    email=email,
                    phone=f"98765{'1' if company_code == 'B' else '0'}{index:04d}",
                    address=[
                        "Delhi, India",
                        "Gurugram, Haryana",
                        "Noida, Uttar Pradesh",
                        "Faridabad, Haryana",
                        "Jaipur, Rajasthan",
                    ][(index - 1) % 5],
                )
            )

    db.flush()

    return (
        db.query(Customer)
        .filter_by(tenant_id=tenant_id)
        .order_by(Customer.id)
        .all()
    )


def get_or_create_vendors(db, tenant_id, company_code):
    locations = [
        "Industrial Area, Faridabad, Haryana",
        "Udyog Vihar, Gurugram, Haryana",
        "Okhla Industrial Area, Delhi",
        "Sector 63, Noida, Uttar Pradesh",
        "Bhiwadi Industrial Area, Rajasthan",
        "Panchkula Industrial Area, Haryana",
    ]

    for index in range(1, 7):
        email = f"vendor{index}_{company_code.lower()}@demo.example.com"

        vendor = db.query(Vendor).filter_by(
            tenant_id=tenant_id,
            email=email,
        ).first()

        if vendor is None:
            db.add(
                Vendor(
                    tenant_id=tenant_id,
                    vendor_name=f"Company {company_code} Vendor {index}",
                    contact_person=f"Contact Person {index}",
                    email=email,
                    phone=f"981100{index:04d}",
                    address=locations[index - 1],
                )
            )

    db.flush()

    return (
        db.query(Vendor)
        .filter_by(tenant_id=tenant_id)
        .order_by(Vendor.id)
        .all()
    )


def create_vendor_items(db, tenant_id, vendors, products):
    for index, product in enumerate(products):
        vendor = vendors[index % len(vendors)]

        existing = db.query(VendorItem).filter_by(
            tenant_id=tenant_id,
            vendor_id=vendor.id,
            inventory_id=product.id,
        ).first()

        if existing is None:
            db.add(
                VendorItem(
                    tenant_id=tenant_id,
                    vendor_id=vendor.id,
                    inventory_id=product.id,
                    purchase_price=product.purchase_price,
                )
            )

    db.flush()


def create_sales_orders(
    db, tenant_id, company_code, customers, products
):
    created = 0

    for month in range(6):
        for order_index in range(10):
            number = month * 10 + order_index + 1
            order_number = f"SO-{company_code}-EXP-{number:03d}"

            existing = db.query(SalesOrder).filter_by(
                tenant_id=tenant_id,
                order_number=order_number,
            ).first()

            if existing:
                continue

            selected = [
                products[(number * 2) % len(products)],
                products[(number * 2 + 1) % len(products)],
            ]

            items = []
            total = Decimal("0.00")

            for position, product in enumerate(selected):
                quantity = 2 + ((number + position) % 8)
                unit_price = Decimal(str(product.selling_price))
                line_total = unit_price * quantity
                total += line_total
                items.append((product, quantity, unit_price, line_total))

            order = SalesOrder(
                tenant_id=tenant_id,
                customer_id=customers[number % len(customers)].id,
                order_number=order_number,
                status="COMPLETED",
                total_amount=total,
                order_date=datetime.now(UTC)
                - timedelta(days=30 * month + order_index * 2),
            )

            db.add(order)
            db.flush()

            for product, quantity, price, line_total in items:
                db.add(
                    SalesOrderItem(
                        tenant_id=tenant_id,
                        sales_order_id=order.id,
                        inventory_id=product.id,
                        quantity=quantity,
                        unit_price=price,
                        line_total=line_total,
                    )
                )

            created += 1

    db.flush()
    return created


def create_purchase_orders(
    db, tenant_id, company_code, vendors, products
):
    created = 0

    for month in range(6):
        for order_index in range(7):
            number = month * 7 + order_index + 1

            if number > 40:
                break

            order_number = f"PO-{company_code}-EXP-{number:03d}"

            existing = db.query(PurchaseOrder).filter_by(
                tenant_id=tenant_id,
                order_number=order_number,
            ).first()

            if existing:
                continue

            selected = [
                products[(number * 3) % len(products)],
                products[(number * 3 + 2) % len(products)],
            ]

            items = []
            total = Decimal("0.00")

            for position, product in enumerate(selected):
                quantity = 10 + ((number + position) % 20) * 5
                unit_cost = Decimal(str(product.purchase_price))
                line_total = unit_cost * quantity
                total += line_total
                items.append(
                    (product, quantity, unit_cost, line_total)
                )

            order = PurchaseOrder(
                tenant_id=tenant_id,
                vendor_id=vendors[number % len(vendors)].id,
                order_number=order_number,
                status="COMPLETED",
                total_amount=total,
                order_date=datetime.now(UTC)
                - timedelta(days=30 * month + order_index * 3),
            )

            db.add(order)
            db.flush()

            for product, quantity, cost, line_total in items:
                db.add(
                    PurchaseOrderItem(
                        tenant_id=tenant_id,
                        purchase_order_id=order.id,
                        inventory_id=product.id,
                        quantity=quantity,
                        unit_cost=cost,
                        line_total=line_total,
                    )
                )

            created += 1

    db.flush()
    return created


def expand_demo_data():
    """Safely add more demo data without deleting existing records."""

    with SessionLocal.begin() as db:
        tenants = {
            tenant.code: tenant
            for tenant in db.query(Tenant).filter(
                Tenant.code.in_(["COMPANY_A", "COMPANY_B"])
            ).all()
        }

        if len(tenants) != 2:
            raise RuntimeError(
                "Both COMPANY_A and COMPANY_B must exist. "
                "Run the original seed first."
            )

        for code, tenant in tenants.items():
            company_code = "A" if code == "COMPANY_A" else "B"

            products = get_or_create_products(
                db, tenant.id, company_code
            )
            customers = get_or_create_customers(
                db, tenant.id, company_code
            )
            vendors = get_or_create_vendors(
                db, tenant.id, company_code
            )

            create_vendor_items(
                db, tenant.id, vendors, products
            )

            sales_created = create_sales_orders(
                db, tenant.id, company_code, customers, products
            )
            purchases_created = create_purchase_orders(
                db, tenant.id, company_code, vendors, products
            )

            print(
                f"Company {company_code}: "
                f"{len(products)} products, "
                f"{len(customers)} customers, "
                f"{len(vendors)} vendors, "
                f"{sales_created} new sales orders, "
                f"{purchases_created} new purchase orders."
            )

    print("Demo data expansion completed successfully.")


if __name__ == "__main__":
    expand_demo_data()