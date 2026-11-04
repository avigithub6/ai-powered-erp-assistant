# AI-Powered ERP Assistant

A multi-tenant ERP assistant project built with Angular, FastAPI, MySQL and Ollama.

This repository is being developed in eight controlled phases. This document describes the implementation completed through **Phase 4** only. Features planned for later phases are not represented as completed.

## Current implementation status

### Completed through Phase 4

- Initial project architecture and backend foundation.
- MySQL database schema and Alembic migration.
- JWT-based authentication and authenticated-user lookup.
- Tenant-aware data access.
- Centralized role-permission definitions.
- Dashboard summary and analytics APIs.
- Sales order list and detail APIs.
- Purchase order list and detail APIs.
- Inventory list and detail APIs.
- Vendor list and detail APIs.
- Customer list and detail APIs.
- Integration and security tests for the implemented APIs.

### Not yet completed

- AI query endpoint and end-to-end AI assistant workflow.
- Later-phase functionality and final ERP integration.
- Final project acceptance and delivery documentation.

The `ai:query` permission is currently present in the permission map, but this does not mean an AI query API has been implemented.

## Technology stack

| Area | Technology |
|---|---|
| Frontend | Angular 21, TypeScript |
| Backend | Python 3.12+, FastAPI |
| ORM | SQLAlchemy 2 |
| Validation | Pydantic |
| Database | MySQL 8, InnoDB |
| Migrations | Alembic |
| Authentication | JWT |
| Password hashing | Argon2 |
| AI model server configuration | Ollama |
| Configured model | qwen2.5:7b-instruct |
| Testing | Pytest |
| Code quality | Ruff |
| Containerization | Docker Compose |

Ollama and the model are part of the project configuration. The Phase 4 API implementation does not yet provide an end-to-end AI query workflow.

## Project structure

```text
AI-powered ERP Assistant/
├── backend/
│   ├── alembic/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── schemas/
│   │   ├── security/
│   │   └── services/
│   ├── tests/
│   │   ├── integration/
│   │   └── security/
│   ├── Dockerfile
│   └── requirements.txt
├── docs/
│   ├── api-contracts.md
│   ├── architecture.md
│   └── security.md
├── frontend/
├── scripts/
├── .env.example
├── docker-compose.yml
└── README.md
```

## Prerequisites

For the Docker-based backend setup:

- Docker Desktop with Docker Compose.
- Git.
- Internet access to download the required container images.

For running the Angular development server separately:

- Node.js and npm.

## Backend setup with Docker Compose

Run these commands from the project root.

### 1. Clone the repository

```powershell
git clone https://github.com/avigithub6/ai-powered-erp-assistant.git
cd ai-powered-erp-assistant
```

### 2. Create the environment file

```powershell
Copy-Item .env.example .env
```

Open `.env` and configure secure values for:

- `MYSQL_PASSWORD`
- `MYSQL_ROOT_PASSWORD`
- `JWT_SECRET_KEY`

Do not use production credentials in a committed environment file. Do not commit `.env`.

The supplied `.env.example` contains local-development configuration. Docker Compose configures the backend database hostname as the MySQL service name.

### 3. Start the containers

```powershell
docker compose up --build -d
```

Check container status:

```powershell
docker compose ps
```

### 4. Apply database migrations

After the backend container is running:

```powershell
docker compose exec backend alembic upgrade head
```

### 5. Download the configured Ollama model

The Compose configuration starts the Ollama service, but does not automatically download the model.

```powershell
docker compose exec ollama ollama pull qwen2.5:7b-instruct
```

Check the downloaded model:

```powershell
docker compose exec ollama ollama list
```

### 6. Verify the backend

Open:

- API root: http://localhost:8000/
- Swagger documentation: http://localhost:8000/docs
- Health endpoint: http://localhost:8000/health

The health endpoint reports backend application health. It should not be treated as proof that every future AI workflow is operational.

## Frontend development server

The Angular application can be run separately:

```powershell
cd frontend
npm install
npm start
```

The frontend development server normally runs at:

http://localhost:4200/

The Phase 4 backend API is available at:

http://localhost:8000/api/v1

Frontend-to-backend integration and final UI workflows should be verified as their implementation progresses.

## API overview

All versioned backend endpoints use the `/api/v1` prefix.

| Area | Endpoints |
|---|---|
| Authentication | `POST /auth/login`, `GET /auth/me` |
| Dashboard | `GET /dashboard/summary` |
| Dashboard analytics | `GET /dashboard/sales-trend`, `GET /dashboard/top-products`, `GET /dashboard/top-vendors` |
| Dashboard inventory | `GET /dashboard/inventory`, `GET /dashboard/low-stock` |
| Sales | `GET /sales`, `GET /sales/{order_id}` |
| Purchases | `GET /purchases`, `GET /purchases/{order_id}` |
| Inventory | `GET /inventory`, `GET /inventory/{item_id}` |
| Vendors | `GET /vendors`, `GET /vendors/{vendor_id}` |
| Customers | `GET /customers`, `GET /customers/{customer_id}` |

For request parameters, response fields and permission requirements, see [API Contracts](docs/api-contracts.md).

## Business rules implemented through Phase 4

- Business data queries are scoped to the authenticated user's tenant.
- Dashboard sales and purchase financial totals use orders whose status is `COMPLETED`.
- Dashboard sales order count includes completed sales orders only.
- Sales and purchase list endpoints can return orders of different statuses; they are not restricted to completed orders.
- Sales and purchase date filters use `order_date` with inclusive start and end boundaries.
- Low stock means `stock_level <= reorder_level`.
- Inventory list endpoints return active inventory records.
- Sales Executive inventory responses exclude procurement purchase-price information.
- Procurement-authorized inventory responses include `purchase_price`.
- Pagination is supported on list endpoints.

## Testing and code quality

Run backend tests from the `backend` directory:

```powershell
cd backend
python -m pytest
```

Run Ruff:

```powershell
python -m ruff check app tests
```

Check formatting errors in Git changes from the repository root:

```powershell
git diff --check
```

**Phase 4 test status:** 51 tests were reported passing during the Phase 4 development workflow. This is the reported result for that development run, not a claim that tests have been rerun on every machine or environment.

## Documentation

- [Architecture](docs/architecture.md)
- [API Contracts](docs/api-contracts.md)
- [Security](docs/security.md)

These documents describe the implementation through Phase 4. They will be expanded and verified as the remaining phases are completed.

## Phase 5 — Angular frontend

Phase 5 adds the Angular frontend and connects it to the implemented FastAPI APIs.

### Implemented frontend features

- Login form using tenant code, username and password.
- JWT authentication through the backend login endpoint.
- Authenticated user lookup through `GET /api/v1/auth/me`.
- Bearer token attachment through an HTTP interceptor.
- Authentication guard for protected application routes.
- Role-based route guards and navigation visibility.
- Dashboard with backend summary and analytics data.
- Sales orders list.
- Purchase orders list.
- Inventory list with low-stock filtering.
- Vendor list.
- Customer list.
- Loading, error, empty-state, refresh and pagination handling on data pages.

### Frontend role navigation

| Role | Available frontend sections |
|---|---|
| Administrator | Dashboard, Sales, Purchases, Inventory, Vendors, Customers |
| Sales Executive | Dashboard, Sales, Inventory, Customers |
| Purchase Executive | Dashboard, Purchases, Inventory, Vendors |
| Management | Dashboard, Sales, Purchases, Inventory, Vendors, Customers |

Frontend role guards and navigation only control the user interface. The FastAPI backend remains responsible for authentication, tenant isolation and permission enforcement.

### Frontend API configuration

During local development, Angular uses the proxy configuration in `frontend/proxy.conf.json` to forward `/api` requests to `http://127.0.0.1:8000`.

The frontend does not send or select a tenant ID for business-data requests. The backend derives tenant identity from the authenticated user.

The JWT access token is stored in browser `sessionStorage`. This is a development implementation and should be reviewed against the deployment security requirements before production use.

### Run the frontend

Open a terminal in the `frontend` directory:

```powershell
npm install
npm start