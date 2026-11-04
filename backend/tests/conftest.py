import pytest
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import Tenant, User
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
        ]

        db.add_all(users)
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
