from app.core.dependencies import require_roles
from app.db.session import get_db
from app.models import User
from app.security.jwt import create_access_token
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient


def test_administrator_role_allowed(db_session):
    test_app = FastAPI()

    def override_get_db():
        yield db_session

    test_app.dependency_overrides[get_db] = override_get_db

    @test_app.get("/admin")
    def admin_endpoint(
        user: User = Depends(require_roles("Administrator")),
    ):
        return {"username": user.username}

    token = create_access_token(
        user_id=1,
        tenant_id=1,
        role="Administrator",
    )

    with TestClient(test_app) as client:
        response = client.get(
            "/admin",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 200
    assert response.json()["username"] == "admin_a"


def test_sales_user_blocked_from_admin_route(db_session):
    test_app = FastAPI()

    def override_get_db():
        yield db_session

    test_app.dependency_overrides[get_db] = override_get_db

    @test_app.get("/admin")
    def admin_endpoint(
        user: User = Depends(require_roles("Administrator")),
    ):
        return {"username": user.username}

    token = create_access_token(
        user_id=2,
        tenant_id=1,
        role="Sales Executive",
    )

    with TestClient(test_app) as client:
        response = client.get(
            "/admin",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 403
