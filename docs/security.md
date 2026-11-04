# Security — Implemented Through Phase 4

## 1. Scope

This document describes authentication, tenant isolation and role-based access controls implemented through Phase 4.

It does not claim that future AI security controls or production Spring Boot service-to-service integration have been completed.

## 2. Authentication

The backend uses JWT Bearer authentication for protected API endpoints.

The authentication dependency:

1. Extracts the Bearer token.
2. Decodes and validates the access token.
3. Reads the user subject and tenant identity from the token.
4. Requires valid positive identity values.
5. Loads the user using both user ID and tenant ID.
6. Requires the user to be active.
7. Loads the corresponding tenant and requires it to be active.
8. Rejects invalid or expired authentication with HTTP 401.

The configured token expiry is 30 minutes by default.

Passwords are handled using Argon2 password hashing. Plain-text passwords must not be stored.

## 3. Tenant isolation

Tenant isolation is a core security requirement.

- Business-data access uses the authenticated user's tenant ID.
- Routers pass the authenticated user's tenant ID to service methods.
- Repositories filter business records by tenant ID.
- Individual record lookups use tenant-scoped queries.
- Tenant-aware relationships and composite constraints are present in the database migration.
- Client-supplied tenant IDs must not override the authenticated tenant context.

The backend must not trust tenant identity supplied through a URL, query parameter, request body, arbitrary header or AI-generated content.

## 4. Role and permission model

The centralized permission map currently defines these roles and permissions.

| Permission | Administrator | Sales Executive | Purchase Executive | Management |
|---|:---:|:---:|:---:|:---:|
| `sales:read` | Yes | Yes | No | Yes |
| `sales:analytics` | Yes | Yes | No | Yes |
| `purchase:read` | Yes | No | Yes | Yes |
| `purchase:analytics` | Yes | No | Yes | Yes |
| `inventory:read` | Yes | Yes | Yes | Yes |
| `inventory:procurement_read` | Yes | No | Yes | Yes |
| `vendors:read` | Yes | No | Yes | Yes |
| `customers:read` | Yes | Yes | No | Yes |
| `dashboard:read` | Yes | Yes | Yes | Yes |
| `ai:query` | Yes | Yes | Yes | Yes |

The `ai:query` permission is defined in the permission map. An AI query endpoint is not part of the Phase 4 API implementation.

The current permission map grants all listed permissions to Administrator and Management.

## 5. Field-level data access

### Sales Executive

Sales Executive has sales read and analytics access, customer read access and general inventory read access.

The base inventory response contains only:

- `id`
- `item_name`
- `sku`
- `category`
- `stock_level`
- `reorder_level`
- `selling_price`
- `unit`

The procurement-specific `purchase_price` field is not included for this role.

### Purchase Executive

Purchase Executive has purchase read and analytics access, vendor read access and procurement inventory access.

The procurement inventory response includes the base inventory fields plus `purchase_price`.

### Administrator and Management

The current permission map grants both roles all defined permissions, including purchase and procurement inventory permissions.

Field visibility is determined by the response schemas and service-level serialization. Do not infer a more restrictive Management permission scope than the one currently implemented.

## 6. Dashboard financial data

Dashboard financial metrics are permission-aware.

- Users without `sales:analytics` do not receive the sales total; their sales order count is set to zero.
- Users without `purchase:analytics` do not receive the purchase total.
- Sales trend and top-product analytics require `sales:analytics`.
- Top-vendor analytics requires `purchase:analytics`.

The dashboard financial calculations use completed orders only.

## 7. Authorization behavior

The centralized role-permission map and service-level checks enforce access rules.

An authenticated user without the required permission receives HTTP 403.

Authentication failures, including invalid or expired tokens and inactive user or tenant records, receive HTTP 401.

## 8. Database protections

The initial migration includes tenant-aware relational constraints and tenant-scoped uniqueness for selected records, including usernames and SKUs.

Monetary columns use `DECIMAL(15,2)` to avoid binary floating-point storage for currency values.

Repositories apply tenant filters to list and detail operations.

## 9. Configuration and secrets

- Keep `.env` out of version control.
- Use strong, unique values for database passwords and JWT signing secrets.
- Do not use example secrets in production.
- Do not expose JWTs in logs or public client-side configuration.
- Restrict access to database and container management credentials.

The `.env.example` file is a configuration template, not a production secrets file.

## 10. Current security boundary

Implemented through Phase 4:

- JWT authentication dependency.
- Active user and tenant validation.
- Tenant-scoped business-data access.
- Centralized role permissions.
- Permission checks on implemented APIs.
- Procurement-specific inventory field control.
- Integration and security tests for the implemented API scope.

Not claimed as completed in Phase 4:

- Production service-to-service authentication with the existing Spring Boot ERP.
- Final trusted identity propagation contract.
- AI prompt-injection defenses and AI-specific authorization.
- Final production security review.

These items must be designed, implemented and verified in their appropriate later phases.
