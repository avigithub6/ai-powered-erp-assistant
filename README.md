# AI-Powered ERP Assistant

An AI-powered, multi-tenant ERP analytics assistant built with **FastAPI, Angular, MySQL, Spring Boot, and Ollama**. It provides secure role-based access to ERP analytics and allows users to ask business questions in natural language.

---

## Project Status

**Core implementation completed and verified.**

The project includes:
- Multi-tenant authentication and authorization.
- Role-based access control (RBAC).
- Company-wise data isolation.
- ERP analytics dashboards.
- Natural-language AI assistant.
- Controlled AI tool execution.
- Read-only database access for AI analytics.
- Spring Boot ERP integration.
- AI query audit logging.
- Automated backend and integration tests.

---

## Technology Stack

| Layer | Technologies |
|---|---|
| Frontend | Angular 21, TypeScript |
| Backend API | Python, FastAPI |
| ERP Integration | Spring Boot 3.5.7, Java 21 |
| Database | MySQL 8.0 |
| ORM | SQLAlchemy 2 |
| Database Migrations | Alembic |
| Validation | Pydantic |
| AI Orchestration | Python, Custom Tool-Based Orchestrator |
| Local LLM | Ollama, Qwen 2.5 1.5B |
| AI Alternative Model | Llama 3.1 8B |
| Containerization | Docker, Docker Compose |
| Testing | Pytest |
| Code Quality | Ruff |

---

## Architecture Overview

```text
                 Users
                   |
                   v
          Angular 21 Frontend
                   |
                   v
             FastAPI Backend
                   |
        +----------+-----------+
        |          |           |
        v          v           v
   Authentication  Analytics  AI Assistant
   & RBAC          Services   Orchestrator
        |          |           |
        |          |           v
        |          |      Ollama LLM
        |          |           |
        |          |      Tool Selection
        |          |           |
        |          |      Validated Tools
        |          |           |
        +----------+-----------+
                   |
                   v
              MySQL 8.0
                   ^
                   |
          Spring Boot ERP
                   |
          Read-Only JDBC Access
                   |
             Sales Orders
```

### Main Components

1. **Angular Frontend:** Provides login, dashboard, analytics, reports, and AI chat interfaces.
2. **FastAPI Backend:** Handles authentication, authorization, tenant isolation, analytics, and AI requests.
3. **Spring Boot ERP Service:** Exposes an authenticated internal API to retrieve ERP sales orders.
4. **MySQL:** Stores users, tenants, sales, purchases, inventory, vendors, and audit records.
5. **Ollama:** Runs the local language model for natural-language question understanding.

---

## Key Features

### 1. Authentication and Role-Based Access Control

- JWT-based authentication.
- Password hashing.
- Server-side role-based authorization.
- Protected API endpoints.
- Separate permissions for different business roles.

### 2. Multi-Tenant Data Isolation

The application supports multiple companies.

- Company A users can access only Company A data.
- Company B users can access only Company B data.
- Tenant ID is derived from the authenticated user.
- Client-provided tenant IDs are not trusted for authorization.
- Database queries are scoped to the authenticated tenant.

### 3. ERP Analytics Dashboard

The dashboard provides business insights such as:

- Total sales.
- Total purchase value.
- Sales order count.
- Top-selling products.
- Top vendors.
- Sales trends.
- Inventory availability.
- Low-stock items.

All metrics are retrieved from persistent database records.

### 4. Natural-Language AI Assistant

Users can ask business questions in natural language.

Supported examples:

- What are the total sales?
- Show the top 5 products.
- Compare sales and purchases over the last 3 months.
- Which products are running low on stock?
- Who are the top vendors?
- Find steel vendors in Delhi NCR.
- Explain the sales trend.

### 5. Controlled AI Tool Execution

The LLM is used for understanding questions and selecting approved tools.

It does not execute arbitrary SQL queries.

The backend validates the selected tool and its arguments before execution.

Approved tools:

| Tool | Purpose |
|---|---|
| `dashboard_summary` | Business summary |
| `sales_trend` | Sales trend analysis |
| `top_products` | Top-selling products |
| `top_vendors` | Top vendors |
| `inventory` | Inventory availability |
| `low_stock` | Low-stock products |
| `sales_purchase_comparison` | Sales and purchase comparison |
| `vendor_search` | Search vendors by material and location |

### 6. AI Database Security

- Separate MySQL read-only account for AI analytics.
- AI account has SELECT-only permissions.
- No INSERT, UPDATE, DELETE, or schema modification permissions.
- Query execution timeout.
- Restricted tool execution.
- Tenant-scoped database access.

### 7. Spring Boot ERP Integration

A working Spring Boot service is integrated with FastAPI.

**Spring Boot service:**
- Spring Boot 3.5.7.
- Java 21.
- Spring JDBC.
- Internal service-token authentication.
- Tenant-scoped sales order queries.
- Dedicated read-only MySQL account.

**Integration flow:**

```text
Angular Frontend
       |
       v
FastAPI Endpoint
       |
       | Internal Service Token
       | Trusted Tenant ID
       v
Spring Boot ERP API
       |
       v
Spring JDBC
       |
       v
MySQL Sales Orders
```

Public FastAPI endpoint:

`GET /api/v1/erp-integration/sales/orders`

Internal Spring Boot endpoint:

`GET /internal/erp/sales/orders`

The authenticated user's tenant ID is passed by the backend. Spring Boot validates the internal service token and applies tenant filtering to database queries.

### 8. AI Query Audit Logging

AI query audit records include:

- Tenant ID.
- User ID.
- User question.
- Selected AI tool.
- Execution source.
- Request status.
- Execution time.
- Error type.
- Creation timestamp.

Successful, failed, and permission-denied AI requests are recorded.

---

## User Roles and Permissions

| Role | Access |
|---|---|
| Administrator | Permitted modules within their own company |
| Sales Executive | Sales and customer-related information |
| Purchase Executive | Purchase, vendor, and procurement information |
| Management | Permitted business summary and analytics |

Access is enforced on the backend. Hiding a frontend page does not replace backend authorization.

### Demo Accounts

All demo accounts use the password:

`Demo@12345`

| Company | Username | Role |
|---|---|---|
| Company A | `admin_a` | Administrator |
| Company A | `sales_a` | Sales Executive |
| Company A | `purchase_a` | Purchase Executive |
| Company A | `manager_a` | Management |
| Company B | `admin_b` | Administrator |
| Company B | `sales_b` | Sales Executive |

Login requires the appropriate tenant code:

- Company A: `COMPANY_A`
- Company B: `COMPANY_B`

Use these credentials only in the local demo environment.

---

## Project Structure

```text
AI-powered-ERP-Assistant/
│
├── backend/
│   ├── alembic/
│   ├── app/
│   │   ├── ai/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── integrations/
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── schemas/
│   │   ├── security/
│   │   └── services/
│   ├── tests/
│   │   ├── integration/
│   │   └── unit/
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   ├── angular.json
│   └── package.json
│
├── spring-boot-erp/
│   ├── src/
│   │   └── main/
│   │       ├── java/
│   │       └── resources/
│   ├── Dockerfile
│   └── pom.xml
│
├── docs/
│   ├── architecture.md
│   ├── api-contracts.md
│   └── security.md
│
├── script/
│   └── test_ai_live.py
│
├── .env.example
├── .gitignore
├── docker-compose.yml
└── README.md
```

---

## Prerequisites

Install the following tools:

- Python 3.12 or compatible project-supported version.
- Node.js and npm.
- Docker Desktop.
- Git.
- Ollama.

For local AI inference, install Ollama and download the configured model.

```powershell
ollama pull qwen2.5:1.5b
```

---

## Environment Configuration

Clone the repository:

```powershell
git clone https://github.com/avigithub6/ai-powered-erp-assistant.git
cd ai-powered-erp-assistant
```

Create your local environment file:

```powershell
Copy-Item .env.example .env
```

Update `.env` with strong local credentials.

Important environment variables:

| Variable | Description |
|---|---|
| `MYSQL_DATABASE` | MySQL database name |
| `MYSQL_USER` | Application database user |
| `MYSQL_PASSWORD` | Application database password |
| `MYSQL_ROOT_PASSWORD` | MySQL root password |
| `DATABASE_URL` | Main application database connection |
| `AI_DATABASE_URL` | AI read-only database connection |
| `OLLAMA_BASE_URL` | Ollama service URL |
| `OLLAMA_MODEL` | Configured local LLM |
| `SPRING_BOOT_ERP_BASE_URL` | Internal Spring Boot service URL |
| `SPRING_BOOT_INTERNAL_TOKEN` | Shared internal service authentication token |
| `SPRING_DB_USER` | Spring Boot read-only database user |
| `SPRING_DB_PASSWORD` | Spring Boot database password |

**Security:** Never commit `.env` or expose actual database passwords, JWT secrets, or internal service tokens.

---

## Database Setup

The application uses MySQL 8.0 with persistent Docker volume storage.

Start the database and application services:

```powershell
docker compose up --build -d
```

Check running services:

```powershell
docker compose ps
```

Run database migrations if they are not automatically applied by the configured startup workflow:

```powershell
docker compose exec backend alembic upgrade head
```

Seed demo data when setting up a fresh database:

```powershell
docker compose exec backend python -m app.db.seed
```

Run these initialization commands only as required by the current database state. Do not reseed an existing database unnecessarily.

---

## Spring Boot Read-Only Database Setup

Spring Boot uses a separate MySQL account with read-only access to sales orders.

Connect to MySQL as root:

```powershell
docker compose exec mysql mysql -uroot -p
```

Create the account and grant the required permission:

```sql
CREATE USER IF NOT EXISTS 'erp_spring_readonly'@'%'
IDENTIFIED BY 'REPLACE_WITH_A_STRONG_PASSWORD';

GRANT SELECT ON erp_assistant.sales_orders
TO 'erp_spring_readonly'@'%';

SHOW GRANTS FOR 'erp_spring_readonly'@'%';
```

Use the actual database name configured in `MYSQL_DATABASE`.

Configure the following variables in `.env`:

```env
SPRING_BOOT_ERP_BASE_URL=http://spring-boot-erp:8080
SPRING_BOOT_INTERNAL_TOKEN=REPLACE_WITH_A_LONG_RANDOM_SECRET
SPRING_DB_USER=erp_spring_readonly
SPRING_DB_PASSWORD=REPLACE_WITH_THE_DATABASE_PASSWORD
```

Use the same internal token for FastAPI and Spring Boot.

Start the Spring Boot service:

```powershell
docker compose up --build -d spring-boot-erp
```

Verify its health:

```powershell
Invoke-RestMethod -Uri "http://localhost:8081/actuator/health"
```

Expected status:

```json
{
  "status": "UP"
}
```

The Spring Boot database account must not receive write or schema modification permissions.

---

## Running the Application

### 1. Start Docker Services

From the repository root:

```powershell
docker compose up --build -d
```

### 2. Start Ollama

Ensure Ollama is running on the host machine.

```powershell
ollama serve
```

If Ollama is already running as a background service, you do not need to start another instance.

Download the configured model if it is not already installed:

```powershell
ollama pull qwen2.5:1.5b
```

### 3. Start Angular Frontend

Open another PowerShell terminal:

```powershell
cd frontend
npm install
npm start
```

Open the frontend using the local URL shown by Angular, normally:

`http://localhost:4200`

### 4. Access Backend API Documentation

FastAPI Swagger UI:

`http://localhost:8000/docs`

FastAPI ReDoc:

`http://localhost:8000/redoc`

Spring Boot health:

`http://localhost:8081/actuator/health`

---

## API Overview

| Module | Endpoint | Access |
|---|---|---|
| Authentication | `/api/v1/auth/login` | Public login |
| Dashboard | `/api/v1/dashboard/summary` | Role-based |
| Sales | `/api/v1/sales` | Sales permissions |
| Purchases | `/api/v1/purchases` | Purchase permissions |
| Vendors | `/api/v1/vendors` | Vendor permissions |
| Inventory | `/api/v1/inventory` | Inventory permissions |
| AI Assistant | `/api/v1/ai/query` | `ai:query` |
| ERP Integration | `/api/v1/erp-integration/sales/orders` | `sales:read` |

All protected FastAPI endpoints require a valid JWT access token.

### Spring Boot Internal API

`GET /internal/erp/sales/orders`

Required headers:

```text
X-Internal-Service-Token: <internal-token>
X-Tenant-Id: <trusted-tenant-id>
```

This endpoint is intended for internal service-to-service communication, not direct public frontend access.

---

## Security Considerations

Security is a core part of this project.

Implemented controls include:

- JWT authentication.
- Password hashing.
- Backend-enforced RBAC.
- Tenant isolation.
- Tenant ID derived from authenticated identity.
- Validated request and response schemas.
- Restricted AI tool allowlist.
- No arbitrary AI-generated SQL execution.
- Separate read-only AI database account.
- Separate read-only Spring Boot database account.
- Internal service-token authentication.
- Tenant-scoped Spring Boot queries.
- Database query execution timeout.
- AI query audit logging.
- Automated security and integration tests.

### Production Hardening

Before production deployment, additional work should include:

- HTTPS and secure reverse-proxy configuration.
- Production secret management.
- Token rotation and expiration policies.
- Database backups and recovery testing.
- Centralized monitoring and alerting.
- Rate limiting and abuse protection.
- Comprehensive audit coverage for all business operations.
- Production deployment and infrastructure security review.

---

## Testing and Verification

Run the complete backend test suite:

```powershell
python -m pytest backend\tests -q
```

Run Spring Boot integration tests:

```powershell
python -m pytest backend\tests\integration\test_erp_integration.py -v
```

Run AI integration tests:

```powershell
python -m pytest backend\tests\integration\test_ai.py -v
```

Run code quality checks:

```powershell
python -m ruff check backend
```

Check frontend production build:

```powershell
cd frontend
npm run build
```

### Recorded Development Verification

The following results were verified during development:

| Verification | Result |
|---|---|
| Backend automated tests | 100 passed |
| AI audit integration tests | 4 passed |
| Spring Boot integration tests | 4 passed |
| Company A/B live tenant integration | Verified |
| AI read-only SELECT access | Verified |
| AI read-only CREATE denial | Verified |
| Spring Boot read-only permissions | Verified |
| Ruff checks for updated integration code | Passed |
| Angular production build | Passed |
| Spring Boot health endpoint | UP |

These are recorded development results; rerun the commands to verify the current checkout.

---

## Documentation

Additional technical documentation:

- `docs/architecture.md` — System architecture and component responsibilities.
- `docs/api-contracts.md` — API endpoints, request/response contracts, and integration details.
- `docs/security.md` — Authentication, authorization, tenant isolation, and database security.

---

## Future Improvements

Potential future enhancements:

- Additional Spring Boot ERP modules and endpoints.
- More advanced AI response evaluation.
- Expanded analytics and reporting.
- Improved dashboard visualizations.
- More comprehensive business-operation audit logging.
- Production deployment automation.
- Performance monitoring and caching.

---

## Author

**Avinash Gupta**

GitHub: [avigithub6](https://github.com/avigithub6)

Repository: [AI-Powered ERP Assistant](https://github.com/avigithub6/ai-powered-erp-assistant)
