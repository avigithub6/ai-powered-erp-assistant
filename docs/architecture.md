# System Architecture

## 1. Overview

The AI-Powered ERP Assistant is a multi-tenant application consisting of:

- Angular 21 frontend.
- FastAPI backend.
- MySQL 8 relational database.
- Ollama-hosted language model.
- Spring Boot ERP integration service.
- Controlled AI tool-execution layer.

The backend is responsible for authentication, authorization, tenant isolation, business logic and database access.

The AI component interprets natural-language questions and selects from a fixed set of approved backend tools. It does not directly query the database.

## 2. High-Level Architecture

```text
+---------------------------+
|     Angular 21 Frontend   |
| Login, Dashboard, ERP UI  |
+-------------+-------------+
              |
              | REST API + JWT
              v
+---------------------------+
|       FastAPI Backend     |
|                           |
|  +---------------------+  |
|  | Authentication      |  |
|  | Authorization       |  |
|  | Tenant Validation   |  |
|  +---------------------+  |
|                           |
|  +---------------------+  |
|  | API Routers         |  |
|  | Auth, Sales,        |  |
|  | Purchase, Inventory |  |
|  | Dashboard, AI       |  |
|  +---------------------+  |
|             |             |
|  +---------------------+  |
|  | Service Layer       |  |
|  +---------------------+  |
|             |             |
|  +---------------------+  |
|  | Repository Layer    |  |
|  +---------------------+  |
+-------------+-------------+
              |
              v
+---------------------------+
|         MySQL 8           |
| Tenant-scoped ERP records |
+---------------------------+

3. Backend Layer Responsibilities
API Layer
FastAPI routers expose versioned REST endpoints under /api/v1.

Responsibilities:
- Validate request data.
- Resolve authenticated users.
- Apply permission dependencies.
- Call the appropriate service.
- Return validated response schemas.
Authentication and Authorization
The authentication layer:
- Validates login credentials.
- Generates JWT access tokens.
- Validates incoming Bearer tokens.
- Resolves the active user and tenant.
- Checks role-based permissions.
Tenant identity is obtained from the authenticated backend user, not from a tenant ID supplied by the frontend or AI model.
Service Layer
Services implement application business logic.

Examples:
- Authentication service.
- Dashboard service.
- Inventory service.
- Sales and purchase services.
- Vendor and customer services.
Services apply business rules and coordinate repository operations.
Repository Layer
Repositories contain database access logic using SQLAlchemy.

Responsibilities:
- Retrieve ERP records.
- Apply tenant filters.
- Perform aggregate calculations.
- Support pagination and filtering.
- Avoid exposing records belonging to other tenants.
4. Database Architecture
The application uses MySQL 8 with InnoDB.

Main database entities include:
Entity    Purpose
tenants    Company or tenant records
users    User accounts and roles
customers    Customer information
inventory    Stock and item information
vendors    Vendor information
vendor_items    Vendor-item relationships
sales_orders    Sales order headers
sales_order_items    Sales order line items
purchase_orders    Purchase order headers
purchase_order_items    Purchase order line items

Business records are associated with tenants. Queries must be scoped to the authenticated user's tenant.

SQLAlchemy models define the relational schema. Alembic manages database migrations.
5. Multi-Tenant Request Flow
Client Request
      |
      v
JWT Bearer Token
      |
      v
Token Validation
      |
      v
Authenticated User
      |
      v
Resolve User Tenant
      |
      v
Check Required Permission
      |
      v
Tenant-Scoped Service
      |
      v
Tenant-Scoped Repository Query
      |
      v
MySQL Result
      |
      v
Validated API Response


The backend must never trust a client-provided tenant ID as the source of authorization context.
6. Role-Based Access Control
Four roles are implemented:
- Administrator
- Sales Executive
- Purchase Executive
- Management
Permissions are defined centrally and checked by backend dependencies and application services.

The general access boundaries are:
Area    Administrator    Sales    Purchase    Management
Dashboard    Yes    Yes    Yes    Yes
Sales    Yes    Yes    No    Yes
Purchase    Yes    No    Yes    Yes
Inventory    Yes    Yes    Yes    Yes
Vendors    Yes    No    Yes    Yes
Customers    Yes    Yes    No    Yes
AI Query    Yes    Yes    Yes    Yes

The exact permissions are documented in security.md.
7. Dashboard Analytics Flow
Dashboard requests follow this path:
Angular Dashboard
       |
       v
Dashboard API
       |
       v
Authentication and Permission Check
       |
       v
Dashboard Service
       |
       v
Dashboard Repository
       |
       v
Tenant-Scoped SQL Aggregations
       |
       v
Dashboard Response


The dashboard calculates values from database records rather than hardcoded demonstration metrics.

Available analytics include:
- Total sales.
- Total purchase value.
- Sales order count.
- Inventory item count.
- Low-stock item count.
- Monthly sales trend.
- Top-selling products.
- Top vendors.
Analytics are permission-aware. Users do not receive restricted business metrics merely because they can access the dashboard.

The sales trend endpoint supports a maximum of 120 records.
8. AI Assistant Architecture
The AI assistant is exposed through:

POST /api/v1/ai/query

Its implementation is organized into:
- API route: backend/app/api/v1/ai.py
- Request and response schemas: backend/app/schemas/ai.py
- Orchestrator: backend/app/ai/orchestrator.py
- Ollama client: backend/app/ai/llm/ollama_client.py
- System prompt: backend/app/ai/prompts/system_prompt.py
- Tool schemas: backend/app/ai/tools/schemas.py
- Tool executor: backend/app/ai/tools/executor.py
AI Request Flow
Natural Language Question
          |
          v
POST /api/v1/ai/query
          |
          v
Authentication and ai:query Permission
          |
          v
AI Orchestrator
          |
          v
Ollama Tool Selection
          |
          v
Pydantic Validation
          |
          v
Approved Tool Executor
          |
          v
Existing ERP Services
          |
          v
Tenant-Scoped Repositories
          |
          v
MySQL
          |
          v
Formatted AI Response


If Ollama is unavailable or its response is invalid, the orchestrator can use a keyword-based fallback classifier.
Approved AI Tools
The tool-selection schema permits only:
Tool    Responsibility
dashboard_summary    Dashboard metrics
sales_trend    Monthly sales trend
top_products    Best-selling products
top_vendors    Vendor purchase ranking
inventory    Inventory information
low_stock    Low-stock items
sales_purchase_comparison    Sales and purchase comparison for the last 90 days
vendor_search    Tenant-scoped vendor search by material and location

Tool arguments are validated using Pydantic. The configured limit is restricted to 1-10.
AI Security Boundary
The language model is not an authorization authority.
- The authenticated user determines tenant identity.
- The authenticated user determines role.
- The backend validates tool selection.
- Existing backend services enforce permissions.
- The tool executor uses approved services and repositories.
- Arbitrary SQL execution is not permitted.
- Inventory results use an explicit response-field allowlist.
- User questions are treated as untrusted input.
The model selects an operation; the backend retrieves and authorizes the actual ERP data.
9. Ollama Deployment
Ollama runs separately on the host machine.

Configured model:

qwen2.5:1.5b

Configured API endpoint:

http://localhost:11434

When the backend runs inside Docker, it connects to the host Ollama service through:

http://host.docker.internal:11434

The Ollama client uses a 20-second request timeout and requests structured JSON output.

Ollama is not started by the project's Docker Compose configuration.
10. Frontend Architecture
The Angular frontend provides:
- Login.
- Dashboard.
- Sales.
- Purchases.
- Inventory.
- Vendors.
- Customers.
Authentication uses an HTTP interceptor to attach the Bearer token to API requests.

Authentication and role-based route guards control frontend navigation. These controls improve the user experience but do not replace backend authorization.

The access token is currently stored in browser sessionStorage.

The current frontend does not include an AI chat interface. AI functionality is available through the backend API.
11. Deployment Architecture
The Docker Compose configuration starts:
- MySQL 8 database.
- FastAPI backend.
The Angular application is started separately using the Angular development server.

Ollama also runs separately on the host machine.
Host Machine
|
+-- Docker Compose
|   |
|   +-- MySQL 8
|   |
|   +-- FastAPI Backend
|
+-- Ollama Service
|
+-- Angular Development Server


This is a local development arrangement, not a production deployment topology.
12. Spring Boot ERP Integration

The project now includes a working Spring Boot ERP integration service.

Spring Boot Integration Components
- Spring Boot 3.5.7 application using Java 21.
- Internal sales orders REST API.
- Spring Boot JDBC integration with MySQL.
- Shared internal service token authentication.
- Tenant identity propagation through X-Tenant-Id.
- Dedicated read-only MySQL database account.

Integration Request Flow

Angular Frontend
       |
       v
FastAPI Backend
       |
       | Authenticated user and permission check
       | Internal service token + trusted tenant ID
       v
Spring Boot ERP Service
       |
       | Validate internal token
       | Validate tenant ID
       v
Sales Order Service
       |
       | Parameterized tenant-scoped SQL
       v
MySQL Database
       |
       v
Validated Response to FastAPI

Internal Spring Boot Endpoint

GET /internal/erp/sales/orders

Supported query parameters:
- limit: 1 to 100, default 20.
- offset: 0 or greater, default 0.

Required headers:
- X-Internal-Service-Token
- X-Tenant-Id

The FastAPI integration endpoint is:

GET /api/v1/erp-integration/sales/orders

FastAPI derives tenant identity from the authenticated user. It does not accept a client-supplied tenant ID as the authorization source.

Security Controls
- Spring Boot validates the internal service token.
- Internal API requests without a valid token are rejected.
- Tenant ID must be a positive integer.
- Sales order queries always filter by tenant_id.
- SQL queries use parameterized values.
- Spring Boot connects using a dedicated MySQL account with SELECT permission only on sales_orders.
- FastAPI enforces sales:read permission before calling Spring Boot.
- Timeouts and upstream HTTP errors are handled by the integration client.
- Integration tests verify Company A and Company B isolation and role restrictions.

Docker Deployment

Docker Compose includes:
- MySQL 8.
- FastAPI backend.
- Spring Boot ERP service.

The Spring Boot service listens on port 8080 inside Docker and is published on localhost port 8081 for local development.

Refer to api-contracts.md for API details and security.md for authorization and database permission rules.

13. Technology Summary
Component    Technology
Frontend    Angular 21
Language    TypeScript
Backend    Python 3.12+, FastAPI
ERP Integration    Spring Boot 3.5.7, Java 21
ERP Database Access    Spring JDBC
ORM    SQLAlchemy 2
Validation    Pydantic
Database    MySQL 8, InnoDB
Migrations    Alembic
Authentication    JWT Bearer
Password Hashing    Argon2
AI Runtime    Ollama
AI Model    qwen2.5:1.5b
Containers    Docker Compose
Backend Testing    Pytest
Linting    Ruff
