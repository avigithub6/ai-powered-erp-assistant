# API Contracts — Phase 4

## 1. Scope and conventions

This document describes the backend endpoints implemented through Phase 4.

Base URL for local development:

```text
http://localhost:8000/api/v1
```

All endpoints below are relative to `/api/v1`.

Protected endpoints require:

```http
Authorization: Bearer <access_token>
```

The authenticated user's tenant identity is resolved by the backend from the validated token and user record. Clients must not choose a tenant by supplying a tenant ID in a business-data request.

## 2. Authentication

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/auth/login` | Authenticate a user and obtain an access token |
| GET | `/auth/me` | Return the authenticated user's information |

The login request uses the configured authentication schema, including tenant code, username and password.

Example request shape:

```json
{
  "tenant_code": "COMPANY_A",
  "username": "admin_a",
  "password": "your-password"
}
```

Use actual provisioned credentials for the environment. Do not assume demo users have been seeded unless the database setup confirms it.

## 3. Dashboard APIs

All dashboard endpoints require the relevant dashboard or analytics permission.

| Method | Endpoint | Permission |
|---|---|---|
| GET | `/dashboard/summary` | `dashboard:read` |
| GET | `/dashboard/sales-trend` | `sales:analytics` |
| GET | `/dashboard/top-products` | `sales:analytics` |
| GET | `/dashboard/top-vendors` | `purchase:analytics` |
| GET | `/dashboard/inventory` | `inventory:read` |
| GET | `/dashboard/low-stock` | `inventory:read` |

### Query parameters

| Endpoint | Parameter | Default | Validation |
|---|---|---:|---|
| `/dashboard/top-products` | `limit` | 5 | 1–100 |
| `/dashboard/top-vendors` | `limit` | 5 | 1–100 |
| `/dashboard/inventory` | `limit` | 20 | 1–100 |
| `/dashboard/inventory` | `offset` | 0 | 0 or greater |
| `/dashboard/low-stock` | `limit` | 20 | 1–100 |
| `/dashboard/low-stock` | `offset` | 0 | 0 or greater |

### Summary response fields

The summary schema includes:

- `total_sales`
- `total_purchase_value`
- `sales_order_count`
- `inventory_item_count`
- `low_stock_count`

Financial fields are permission-aware. Users without sales analytics access do not receive the sales total and have the sales order count set to zero. Users without purchase analytics access do not receive the purchase total.

Other dashboard response schemas include monthly sales trend items, top products, top vendors and paginated inventory data.

## 4. Sales APIs

| Method | Endpoint | Permission |
|---|---|---|
| GET | `/sales` | `sales:read` |
| GET | `/sales/{order_id}` | `sales:read` |

List query parameters:

| Parameter | Default | Description |
|---|---:|---|
| `limit` | 20 | Page size, 1–100 |
| `offset` | 0 | Number of records to skip, 0 or greater |
| `start_date` | None | Inclusive lower bound for `order_date` |
| `end_date` | None | Inclusive upper bound for `order_date` |

The list response contains:

- `items`
- `total`
- `limit`
- `offset`

Sales order response fields:

- `id`
- `customer_id`
- `order_number`
- `status`
- `total_amount`
- `order_date`

The detail response additionally contains `items`, with:

- `id`
- `inventory_id`
- `quantity`
- `unit_price`
- `line_total`

The list endpoint is not restricted to completed orders. Completed-only filtering is applied to dashboard financial analytics.

## 5. Purchase APIs

| Method | Endpoint | Permission |
|---|---|---|
| GET | `/purchases` | `purchase:read` |
| GET | `/purchases/{order_id}` | `purchase:read` |

List query parameters:

| Parameter | Default | Description |
|---|---:|---|
| `limit` | 20 | Page size, 1–100 |
| `offset` | 0 | Number of records to skip, 0 or greater |
| `start_date` | None | Inclusive lower bound for `order_date` |
| `end_date` | None | Inclusive upper bound for `order_date` |

The list response contains `items`, `total`, `limit` and `offset`.

Purchase order response fields:

- `id`
- `vendor_id`
- `order_number`
- `status`
- `total_amount`
- `order_date`

The detail response additionally contains `items`, with:

- `id`
- `inventory_id`
- `quantity`
- `unit_cost`
- `line_total`

The list endpoint is not restricted to completed orders. Completed-only filtering is applied to dashboard purchase-value analytics.

## 6. Inventory APIs

| Method | Endpoint | Permission |
|---|---|---|
| GET | `/inventory` | `inventory:read` |
| GET | `/inventory/{item_id}` | `inventory:read` |

List query parameters:

| Parameter | Default | Description |
|---|---:|---|
| `limit` | 20 | Page size, 1–100 |
| `offset` | 0 | Number of records to skip, 0 or greater |
| `low_stock_only` | false | Return only low-stock items when true |

The base sales inventory response contains exactly these fields:

- `id`
- `item_name`
- `sku`
- `category`
- `stock_level`
- `reorder_level`
- `selling_price`
- `unit`

For users with `inventory:procurement_read`, the procurement response additionally includes `purchase_price`.

The list response contains `items`, `total`, `limit` and `offset`.

Low-stock logic:

```text
stock_level <= reorder_level
```

Only active inventory records are included.

## 7. Vendor APIs

| Method | Endpoint | Permission |
|---|---|---|
| GET | `/vendors` | `vendors:read` |
| GET | `/vendors/{vendor_id}` | `vendors:read` |

List query parameters:

- `limit`: default 20, range 1–100.
- `offset`: default 0, minimum 0.

Vendor response fields:

- `id`
- `vendor_name`
- `contact_person`
- `email`
- `phone`
- `address`

The list response contains `items`, `total`, `limit` and `offset`.

## 8. Customer APIs

| Method | Endpoint | Permission |
|---|---|---|
| GET | `/customers` | `customers:read` |
| GET | `/customers/{customer_id}` | `customers:read` |

List query parameters:

- `limit`: default 20, range 1–100.
- `offset`: default 0, minimum 0.

Customer response fields:

- `id`
- `name`
- `email`
- `phone`
- `address`

The list response contains `items`, `total`, `limit` and `offset`.

## 9. Date and financial calculation rules

- Date filters apply to the relevant order's `order_date`.
- Start and end date boundaries are inclusive.
- A start date later than the end date is rejected with HTTP 400.
- Dashboard sales financial calculations include only sales orders with status `COMPLETED`.
- Dashboard purchase financial calculations include only purchase orders with status `COMPLETED`.
- Sales and purchase list endpoints may return other statuses.

## 10. Common HTTP behavior

The API uses standard HTTP status codes for authentication, authorization and request validation.

| Status | Meaning |
|---|---|
| 200 | Request completed |
| 400 | Invalid business filter, such as start date later than end date |
| 401 | Missing, invalid or expired authentication |
| 403 | Authenticated user lacks the required permission |
| 422 | Request validation error |

The exact error response body is defined by the FastAPI exception handling and validation behavior in the running application.

## 11. Existing ERP integration boundary

The target ERP environment uses Java Spring Boot, MySQL and Angular. The Phase 4 backend exposes REST APIs that can be evaluated for integration.

A production integration contract still needs to be finalized and verified in a later phase. In particular, service-to-service authentication, trusted identity propagation, deployment topology, token issuance and production error mapping must not be assumed to be implemented merely because the REST endpoints exist.

The Spring Boot application must not be allowed to set an arbitrary tenant identity for business-data access. Tenant identity must be validated through a trusted authentication mechanism.