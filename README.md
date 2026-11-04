# AI-Powered ERP Assistant

A multi-tenant ERP analytics and AI assistant built with Angular 21, FastAPI, MySQL 8 and Ollama.

The application provides role-based ERP dashboards, sales and purchase analytics, inventory visibility, tenant isolation and natural-language queries through a controlled AI tool-execution layer.

## Project Status

| Phase | Scope | Status |
|---|---|---|
| Phase 1 | Project foundation and database schema | Completed |
| Phase 2 | Authentication and tenant isolation | Completed |
| Phase 3 | Role-based permissions and business APIs | Completed |
| Phase 4 | Dashboard analytics and backend integration tests | Completed |
| Phase 5 | Angular frontend | Completed |
| Phase 6 | AI assistant and controlled tool integration | Completed |
| Phase 7 | Final documentation and submission readiness audit | In progress |

## Technology Stack

### Frontend
- Angular 21
- TypeScript
- SCSS
- RxJS
- Angular Router and HTTP Interceptors

### Backend
- Python 3.12+
- FastAPI
- SQLAlchemy 2
- Pydantic
- Alembic
- HTTPX

### Database
- MySQL 8
- InnoDB
- Tenant-aware relational schema

### AI
- Ollama
- `qwen2.5:1.5b`
- Pydantic-validated tool selection
- Controlled backend tool execution
- Keyword-based fallback when the LLM is unavailable or returns an invalid response

### Security and Quality
- JWT Bearer authentication
- Argon2 password hashing
- Centralized role-permission definitions
- Tenant-scoped database queries
- Pytest
- Ruff
- Docker Compose

## Architecture Overview

```text
Angular 21 Frontend
        |
        | HTTP / REST + JWT
        v
FastAPI Backend
        |
        +----------------------+
        |                      |
        v                      v
 Authentication          ERP API Routers
 and Authorization             |
        |                       |
        |                 Service Layer
        |                       |
        |                 Repository Layer
        |                       |
        |                       v
        |                    MySQL 8
        |
        v
 AI Query Endpoint
        |
        v
 AI Orchestrator
        |
        +----------------------+
        |                      |
        v                      v
   Ollama LLM             Fallback Classifier
        |                      |
        +----------+-----------+
                   |
                   v
          Validated Tool Selection
                   |
                   v
             Tool Executor
                   |
                   v
       Authorized Backend Services
                   |
                   v
                 MySQL

The AI model selects an approved tool. The backend validates the selection, enforces permissions and retrieves data through existing services and repositories. The model does not execute arbitrary SQL or directly access the database.
Main Features
Authentication
- Login using tenant code, username and password.
- JWT access token generation.
- Authenticated user profile endpoint.
- Active user and tenant validation.
- Argon2 password hashing.
Multi-Tenant Data Isolation
- Business data is scoped to the authenticated user's tenant.
- Tenant identity is derived from the validated backend user.
- Client-supplied tenant IDs cannot override the authenticated tenant context.
- Individual record lookups use tenant-scoped queries.
Role-Based Access Control
Four application roles are implemented:
Role    Access
Administrator    All defined ERP permissions
Sales Executive    Sales, customers, dashboard and general inventory
Purchase Executive    Purchases, vendors, dashboard and procurement inventory
Management    All defined ERP permissions and analytics

The backend enforces permissions. Frontend route guards and navigation visibility are user-interface controls only.
ERP APIs
- Authentication and user profile.
- Dashboard summary and analytics.
- Sales orders.
- Purchase orders.
- Inventory.
- Vendors.
- Customers.
Dashboard Analytics
- Total sales.
- Total purchase value.
- Completed sales order count.
- Inventory item count.
- Low-stock item count.
- Monthly sales trend.
- Top-selling products.
- Top vendors.
- Paginated inventory and low-stock records.
Financial dashboard calculations use completed orders only. Sales and purchase list endpoints can return orders with other statuses.
AI Assistant
The AI assistant accepts natural-language ERP questions through:

POST /api/v1/ai/query

Example request:
{
  "question": "Show me the low stock items"
}


The request accepts a question between 2 and 1000 characters and rejects additional fields.

The response schema contains:
- answer
- tool_used
- source
- data
The assistant supports six approved tools:
Tool    Purpose
dashboard_summary    Overall dashboard metrics
sales_trend    Monthly sales trend
top_products    Best-selling products
top_vendors    Vendor purchase ranking
inventory    Inventory and available stock
low_stock    Items requiring reorder attention

AI execution safeguards:
- Ollama returns structured JSON for tool selection.
- Pydantic validates the selected tool and arguments.
- Only the six approved tools can be selected.
- Tool limits are restricted to 1–10.
- The backend supplies tenant identity and role from the authenticated user.
- Existing backend services enforce the relevant permissions.
- Inventory output uses an explicit field allowlist and excludes procurement-only fields.
- The system prompt treats the user question as untrusted input.
- Ollama requests use a 20-second timeout.
- Keyword-based fallback selection is available if Ollama is unavailable or its response is invalid.
- The model does not generate business figures or execute SQL.
The source response field identifies whether tool selection came from ollama or fallback.
Repository Structure
AI-powered ERP Assistant/
|
+-- backend/
|   +-- app/
|   |   +-- ai/
|   |   |   +-- llm/
|   |   |   +-- prompts/
|   |   |   +-- tools/
|   |   |   +-- orchestrator.py
|   |   +-- api/
|   |   +-- core/
|   |   +-- db/
|   |   +-- models/
|   |   +-- repositories/
|   |   +-- schemas/
|   |   +-- services/
|   +-- alembic/
|   +-- tests/
|   +-- Dockerfile
|
+-- frontend/
|   +-- src/
|   +-- package.json
|   +-- proxy.conf.json
|
+-- docs/
|   +-- architecture.md
|   +-- api-contracts.md
|   +-- security.md
|
+-- docker-compose.yml
+-- .env.example
+-- .gitignore
+-- README.md


Prerequisites
Install the following:
- Python 3.12 or later.
- Node.js and npm compatible with the Angular 21 project.
- Docker Desktop with Docker Compose.
- Ollama installed on the host machine.
- Git.
Environment Configuration
Create the local environment file:
Copy-Item .env.example .env


Update .env with appropriate local values.

Important settings:
Variable    Purpose
APP_NAME    Application name
APP_VERSION    Application version
API_V1_PREFIX    Backend API prefix
DEBUG    Debug mode; disable in production
MYSQL_DATABASE    MySQL database name
MYSQL_USER    MySQL application user
MYSQL_PASSWORD    MySQL application password
MYSQL_ROOT_PASSWORD    MySQL root password
DATABASE_URL    Local database connection URL
OLLAMA_BASE_URL    Ollama endpoint
OLLAMA_MODEL    Ollama model name
JWT_SECRET_KEY    JWT signing secret
JWT_ALGORITHM    JWT signing algorithm
JWT_ACCESS_TOKEN_EXPIRE_MINUTES    JWT lifetime in minutes

The Docker Compose backend database URL uses MYSQL_PASSWORD_URLENCODED. Define this variable in .env with the URL-encoded form of the database password, especially when it contains reserved URL characters.

Use strong, unique secrets. Never commit .env or production credentials.
Run the Application
1. Start Ollama on the host
Ollama is not a Docker Compose service in this project. It runs separately on the host machine.

Pull the configured model:
ollama pull qwen2.5:1.5b


Verify the model:
ollama list


Make sure the Ollama service is running and accessible at:

http://localhost:11434

The Dockerized backend connects to the host Ollama service through:

http://host.docker.internal:11434
2. Start MySQL and the backend
From the repository root:
docker compose up --build -d


Check service status:
docker compose ps


View backend logs:
docker compose logs -f backend


3. Apply database migrations
docker compose exec backend alembic upgrade head


Check the current migration:
docker compose exec backend alembic current


4. Start the Angular frontend
Open another terminal:
cd frontend
npm install
npm start


The development server normally runs at:

http://localhost:4200/
5. Access the backend
API base URL:

http://localhost:8000/api/v1

Interactive API documentation:

http://localhost:8000/docs

Health endpoint:

http://localhost:8000/health

The Angular development proxy forwards /api requests to the local FastAPI backend.
Demo Data and Credentials
The project uses synthetic demonstration data for testing multi-tenant access.

The seeded demonstration accounts are:
Tenant    Username    Role
COMPANY_A    admin_a    Administrator
COMPANY_A    sales_a    Sales Executive
COMPANY_A    purchase_a    Purchase Executive
COMPANY_A    manager_a    Management
COMPANY_B    admin_b    Administrator
COMPANY_B    sales_b    Sales Executive

Demonstration password:

Demo@12345

These are development-only credentials. Do not use them in production. Confirm that the seed operation has been run before attempting login.
API Overview
All versioned endpoints use /api/v1.
Area    Method and endpoints    Permission
Authentication    POST /auth/login, GET /auth/me    Login / authenticated user
Dashboard    GET /dashboard/summary    dashboard:read
Sales analytics    GET /dashboard/sales-trend, GET /dashboard/top-products    sales:analytics
Purchase analytics    GET /dashboard/top-vendors    purchase:analytics
Inventory analytics    GET /dashboard/inventory, GET /dashboard/low-stock    inventory:read
Sales    GET /sales, GET /sales/{order_id}    sales:read
Purchases    GET /purchases, GET /purchases/{order_id}    purchase:read
Inventory    GET /inventory, GET /inventory/{item_id}    inventory:read
Vendors    GET /vendors, GET /vendors/{vendor_id}    vendors:read
Customers    GET /customers, GET /customers/{customer_id}    customers:read
AI Assistant    POST /ai/query    ai:query

See API Contracts for request parameters, response fields and authorization details.
Frontend
The Angular frontend provides:
- Login using tenant code, username and password.
- JWT authentication and authenticated user lookup.
- Bearer token HTTP interceptor.
- Authentication and role-based route guards.
- Role-aware application navigation.
- Dashboard summary and analytics.
- Sales orders list.
- Purchase orders list.
- Inventory list and low-stock filtering.
- Vendor list.
- Customer list.
- Loading, error, empty-state, refresh and pagination handling on data pages.
The frontend stores the access token in browser sessionStorage. This is a development implementation and requires production security review.

The current frontend provides read-oriented ERP pages. An AI chat interface and create/update/delete ERP workflows are not claimed as implemented.
Testing and Code Quality
Backend tests
From the repository root:
cd backend
python -m pytest


Ruff
python -m ruff check app tests


Frontend tests
From the frontend directory:
npm test


Frontend production build
npm run build


Git whitespace validation
From the repository root:
git diff --check


Recorded development verification
The development workflow recorded:
- 66 backend tests passing in the full backend suite.
- 15 AI integration tests passing in a separate AI test run.
- 4 authentication tests passing in a separate authentication test run.
- 10 dashboard tests passing in a separate dashboard test run.
- Ruff checks passing.
- 2 frontend tests passing.
- Angular production build passing.
These are recorded results from their respective development runs. Separate test runs may overlap and must not be added together as a unique total. Rerun the commands above in the final environment before submission.
Security Considerations
- Backend authorization is authoritative; frontend role checks are not security boundaries.
- Tenant identity is derived from the authenticated backend user.
- Database queries are tenant-scoped.
- AI tool execution uses an allowlist and existing backend permission checks.
- The AI model cannot execute arbitrary SQL.
- User input is treated as untrusted.
- Authentication and authorization events are logged without logging passwords or JWT tokens.
- .env must remain outside version control.
- Production deployment must use strong secrets, HTTPS, restricted database exposure and appropriate network controls.
- Review browser token storage and XSS protections before production deployment.
See Security for further details and known boundaries.
Spring Boot Integration Boundary
The target ERP environment includes an existing Java Spring Boot application.

This repository provides an independently runnable FastAPI backend and Angular frontend, together with documented REST API contracts.

A completed production integration with the existing Spring Boot ERP is not claimed. Service-to-service authentication, trusted identity propagation, deployment topology and production error mapping require integration-specific implementation and verification.

See API Contracts for the integration boundary.
Documentation
- Architecture
- API Contracts
- Security
License
This repository was prepared as an ERP assistant assignment project. Add the applicable license if required by the project owner.
