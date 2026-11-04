# API Contracts

## 1. Overview

The backend exposes REST APIs using FastAPI.

Base URL:

`http://localhost:8000/api/v1`

Interactive API documentation:

`http://localhost:8000/docs`

Authentication uses JWT Bearer tokens for protected endpoints.

## 2. Authentication

### Login

`POST /api/v1/auth/login`

Authenticates a user using tenant code, username and password.

Example request:

```json
{
  "tenant_code": "COMPANY_A",
  "username": "admin_a",
  "password": "Demo@12345"
}

The successful response contains an access token and token type.

Use the returned token in subsequent protected requests:

Authorization: Bearer <access_token>
Current User
GET /api/v1/auth/me

Returns information about the authenticated user, including the user's role and tenant context.

Requires authentication.
3. Dashboard APIs
All dashboard endpoints require authentication and the corresponding dashboard or analytics permission.
Dashboard Summary
GET /api/v1/dashboard/summary

Permission: dashboard:read

Returns permission-aware summary metrics, including applicable sales, purchase and inventory metrics.
Sales Trend
GET /api/v1/dashboard/sales-trend

Permission: sales:analytics

Query parameters:
Parameter    Type    Default    Constraints
limit    Integer    120    1â€“120

Returns monthly sales trend data for the authenticated tenant.
Top Products
GET /api/v1/dashboard/top-products

Permission: sales:analytics

Returns the top-selling products based on sales records.
Top Vendors
GET /api/v1/dashboard/top-vendors

Permission: purchase:analytics

Returns vendor purchase ranking for the authenticated tenant.
Inventory Analytics
GET /api/v1/dashboard/inventory

Permission: inventory:read

Returns inventory summary information.
Low Stock Analytics
GET /api/v1/dashboard/low-stock

Permission: inventory:read

Returns inventory items requiring reorder attention.
4. Sales APIs
Permission: sales:read
Method    Endpoint    Purpose
GET    /api/v1/sales    List sales orders
GET    /api/v1/sales/{order_id}    Retrieve a sales order

Sales analytics additionally require sales:analytics.

Responses are scoped to the authenticated tenant.
5. Purchase APIs
Permission: purchase:read
Method    Endpoint    Purpose
GET    /api/v1/purchases    List purchase orders
GET    /api/v1/purchases/{order_id}    Retrieve a purchase order

Purchase analytics additionally require purchase:analytics.

Responses are scoped to the authenticated tenant.
6. Inventory APIs
Permission: inventory:read
Method    Endpoint    Purpose
GET    /api/v1/inventory    List inventory items
GET    /api/v1/inventory/{item_id}    Retrieve an inventory item

Procurement-specific inventory information additionally requires inventory:procurement_read.
7. Vendor APIs
Permission: vendors:read
Method    Endpoint    Purpose
GET    /api/v1/vendors    List vendors
GET    /api/v1/vendors/{vendor_id}    Retrieve a vendor

Vendor information is restricted to roles with the required permission.
8. Customer APIs
Permission: customers:read
Method    Endpoint    Purpose
GET    /api/v1/customers    List customers
GET    /api/v1/customers/{customer_id}    Retrieve a customer

Customer information is restricted to roles with the required permission.
9. AI Assistant API
Natural Language ERP Query
POST /api/v1/ai/query

Permission: ai:query

The endpoint accepts a natural-language question and uses the AI orchestrator to select an approved backend tool.

Request:
{
  "question": "Show me the low stock items"
}


Request validation:
Field    Type    Validation
question    String    Minimum 2 characters
question    String    Maximum 1000 characters
Additional fields    Not allowed    Rejected

Response structure:
{
  "answer": "Low stock inventory information...",
  "tool_used": "low_stock",
  "source": "ollama",
  "data": []
}


The example values illustrate the response structure; actual answer and data depend on the database and selected tool.

Response fields:
Field    Type    Description
answer    String    Formatted answer
tool_used    String or null    Approved tool selected
source    String    ollama or fallback
data    Any    Authorized backend result

Supported AI Tools
Tool    Description
dashboard_summary    Dashboard summary
sales_trend    Monthly sales trend
top_products    Best-selling products
top_vendors    Vendor purchase ranking
inventory    Inventory information
low_stock    Low-stock inventory
sales_purchase_comparison    Sales and purchase comparison for the last 90 days
vendor_search    Tenant-scoped vendor search by material and location

Tool arguments are validated by Pydantic. The supported result limit is between 1 and 10.
AI Execution and Authorization
The AI model only selects an approved operation.

The backend:
1. Authenticates the request.
2. Checks ai:query permission.
3. Obtains tenant ID and role from the authenticated user.
4. Validates the selected tool and arguments.
5. Executes the approved backend service.
6. Applies existing role permissions and tenant filters.
7. Returns authorized data.
The AI model cannot supply a trusted tenant ID or role, execute arbitrary SQL or bypass backend authorization.

If Ollama is unavailable or returns an invalid response, the orchestrator can use the keyword-based fallback classifier.
10. Permission Matrix
Permission    Administrator    Sales    Purchase    Management
dashboard:read    Yes    Yes    Yes    Yes
sales:read    Yes    Yes    No    Yes
sales:analytics    Yes    Yes    No    Yes
purchase:read    Yes    No    Yes    Yes
purchase:analytics    Yes    No    Yes    Yes
inventory:read    Yes    Yes    Yes    Yes
inventory:procurement_read    Yes    No    Yes    Yes
vendors:read    Yes    No    Yes    Yes
customers:read    Yes    Yes    No    Yes
ai:query    Yes    Yes    Yes    Yes

All business data access is restricted to the authenticated user's tenant.
11. Common HTTP Status Codes
Status    Meaning
200    Request successful
400    Invalid or unsupported operation
401    Authentication required or invalid
403    Permission denied
404    Requested record not found
422    Request validation failed
500    Internal server error

Actual error response details depend on the endpoint and exception handler.
12. Pagination and Filtering
List endpoints support the pagination and filtering parameters defined by their request handlers.

Clients should use the documented endpoint schema in /docs as the authoritative reference for available query parameters and response structure.

The dashboard sales-trend endpoint supports limit from 1 through 120.
13. Spring Boot ERP Integration Contract

The project includes a working integration between FastAPI and a Spring Boot ERP service.

FastAPI Public Endpoint

GET /api/v1/erp-integration/sales/orders

Permission: sales:read

Authentication: JWT Bearer token

Query parameters:
Parameter    Type    Default    Constraints
limit    Integer    20    1-100
offset    Integer    0    0 or greater

FastAPI obtains the tenant ID from the authenticated user. The client cannot select another tenant by passing a tenant ID.

Response structure:
{
  "items": [
    {
      "id": 1,
      "order_number": "SO-A-001",
      "status": "confirmed",
      "total_amount": "15000.00",
      "order_date": "2026-11-05T10:00:00"
    }
  ],
  "total": 1,
  "limit": 20,
  "offset": 0
}

The response contains sales orders returned by the Spring Boot service for the authenticated tenant.

Internal Spring Boot Endpoint

GET /internal/erp/sales/orders

Query parameters:
- limit: 1-100, default 20.
- offset: 0 or greater, default 0.

Required internal headers:
- X-Internal-Service-Token
- X-Tenant-Id

The internal endpoint is intended for service-to-service communication, not direct public client access.

Integration Security
1. FastAPI authenticates the user and checks sales:read permission.
2. FastAPI obtains tenant ID from the authenticated user.
3. FastAPI sends the internal service token and trusted tenant ID to Spring Boot.
4. Spring Boot validates the internal token and tenant ID.
5. Spring Boot queries sales_orders using a parameterized tenant-scoped SQL query.
6. Spring Boot uses a dedicated MySQL account with SELECT-only access to sales_orders.
7. FastAPI validates the upstream response before returning it.

Error handling:
- Invalid internal token: 401 from Spring Boot.
- Invalid tenant header: 400 from Spring Boot.
- Upstream timeout or service failure: handled by FastAPI integration endpoint.

The Spring Boot service listens on port 8080 inside Docker and is published on localhost port 8081 for local development.
14. API Verification
Start the backend and open:

http://localhost:8000/docs

Use the interactive API documentation to inspect:
- Request schemas.
- Response schemas.
- Query parameters.
- Authentication requirements.
- Available endpoints.
For automated backend verification:
cd backend
python -m pytest
