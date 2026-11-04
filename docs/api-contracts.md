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
limit    Integer    120    1–120

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
13. Spring Boot Integration Contract
This project documents a REST integration boundary for an existing Spring Boot ERP environment.

The FastAPI service can be called by another backend using HTTP and the documented request/response contracts.

A production integration requires agreement on:
- Service-to-service authentication.
- Trusted user and tenant identity propagation.
- Authorization responsibility.
- Network and gateway configuration.
- Error mapping and timeout behavior.
- Integration testing against the actual Spring Boot application.
This repository does not claim that a live Spring Boot integration has already been deployed.
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
