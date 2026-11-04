# Architecture — Implemented Through Phase 4

## 1. Scope

This document records the architecture implemented through Phase 4 of the AI-Powered ERP Assistant project.

The project is being developed in eight phases. This document does not describe planned later-phase features as completed functionality.

The target environment includes an existing ERP platform using Java Spring Boot, MySQL and Angular. The current repository provides an independent FastAPI backend and an Angular project. A complete production integration with the existing ERP is not claimed at this stage.

## 2. Technology stack

### Frontend
- Angular 21
- TypeScript
- SCSS

### Backend
- Python 3.12+
- FastAPI
- SQLAlchemy 2
- Pydantic
- Alembic

### Database
- MySQL 8
- InnoDB
- Tenant-aware relational schema

### Authentication and security
- JWT access tokens
- Argon2 password hashing
- Centralized role-permission definitions
- Tenant-scoped repository queries

### Infrastructure and testing
- Docker Compose
- Pytest
- Ruff

### AI configuration
The project configuration includes Ollama and `qwen2.5:7b-instruct`. The AI query API and end-to-end assistant workflow are not part of the completed Phase 4 implementation.

## 3. High-level architecture

```text
                 Angular Frontend
                        |
                        | HTTP / REST
                        v
                 FastAPI Application
                        |
             +----------+----------+
             |          |          |
             v          v          v
        Authentication  API      Permission
          and JWT      Routers    Checks
             |          |
             |          v
             |       Services
             |          |
             |          v
             |     Repositories
             |          |
             +----------+
                        |
                        v
                    MySQL 8
```

The diagram represents the implemented Phase 4 request and data-access flow. It does not imply that the AI assistant workflow is already connected.

## 4. Backend layers

### API routers

The versioned API routers are registered under `/api/v1`.

Implemented areas:

- Authentication
- Dashboard
- Sales
- Purchases
- Inventory
- Vendors
- Customers

Routers validate request parameters, obtain the authenticated user and pass the user's tenant identity and role to the service layer.

### Core security and permissions

The authentication dependency validates the JWT and loads an active user within the token's tenant. The tenant must also be active.

A centralized permission map defines access by role. Services check the permissions required for their operations.

### Service layer

Services contain business-level authorization and validation.

Examples:

- Dashboard services enforce analytics permissions.
- Sales and purchase services validate date ranges.
- Inventory services control whether procurement-specific fields are included.
- Vendor and customer services apply their respective read permissions.

### Repository layer

Repositories perform database access using SQLAlchemy.

Business-data repository operations use the authenticated tenant ID as a filter. List operations apply pagination and supported filters.

## 5. Database structure

The initial database migration creates these ten business and identity tables:

1. `tenants`
2. `users`
3. `customers`
4. `inventory`
5. `vendors`
6. `vendor_items`
7. `sales_orders`
8. `sales_order_items`
9. `purchase_orders`
10. `purchase_order_items`

The schema uses MySQL InnoDB, tenant-aware relationships and composite tenant constraints where defined in the migration.

Important database design characteristics include:

- Tenant-scoped username uniqueness.
- Tenant-scoped SKU uniqueness.
- Tenant-aware order and order-item relationships.
- `DECIMAL(15,2)` for monetary values.
- Alembic-managed schema migration.

## 6. Authentication and request flow

1. A client sends login credentials to the authentication endpoint.
2. The backend validates the credentials.
3. The backend issues a JWT access token after successful authentication.
4. The client sends the token using the Bearer authorization scheme.
5. The authentication dependency validates the token and loads the active user and tenant.
6. The router passes the authenticated user's tenant ID and role to the service.
7. The service checks the required permission.
8. The repository executes tenant-scoped database queries.
9. The service returns validated response data.

Tenant identity for business-data access is derived from the authenticated server-side user, not from a client-supplied tenant filter.

## 7. Dashboard calculation rules

Dashboard financial metrics use completed records only.

- Total sales: sum of `total_amount` for the tenant's completed sales orders.
- Total purchase value: sum of `total_amount` for the tenant's completed purchase orders.
- Sales order count: count of completed sales orders.
- Inventory item count: count of active inventory records.
- Low-stock count: active inventory records where `stock_level <= reorder_level`.
- Sales trend: monthly aggregation of completed sales orders using `order_date`.
- Top products: completed sales order items grouped by inventory item and summed by quantity.
- Top vendors: completed purchase orders grouped by vendor and summed by purchase value.

The sales and purchase list APIs are not restricted to completed orders. They return records matching their tenant, date and pagination filters.

## 8. Role-based data access

The permission map currently defines these roles:

- `Administrator`
- `Sales Executive`
- `Purchase Executive`
- `Management`

Sales and purchase analytics, inventory procurement fields, vendor data and customer data are protected by their respective permissions.

The current permission map grants all defined permissions to Administrator and Management. The Sales Executive and Purchase Executive have different access scopes. See [Security](security.md) for the Phase 4 permission matrix.

## 9. Current implementation boundary

Completed through Phase 4:

- Database foundation and migration.
- Authentication and tenant-aware user lookup.
- Centralized permission definitions.
- Dashboard, sales, purchases, inventory, vendors and customers APIs.
- Integration and security test coverage for these APIs.

Not represented as completed:

- AI query endpoint.
- End-to-end RAG or AI assistant workflow.
- Full production integration with the existing Spring Boot ERP.
- Final project acceptance and delivery.

The architecture documentation will be expanded after subsequent phases are implemented and verified.

10. Phase 5 — Angular frontend architecture
Phase 5 implements the Angular client for the existing FastAPI APIs.
Frontend structure
The Angular application uses standalone components and is organized into:
- core/auth: authentication-related functionality.
- core/guards: authentication and role-based route guards.
- core/interceptors: HTTP authentication interceptor.
- core/models: authentication, dashboard and ERP response models.
- core/services: authentication, dashboard and ERP API services.
- features/auth: login page.
- features/dashboard: dashboard page.
- features/sales: sales orders page.
- features/purchases: purchase orders page.
- features/inventory: inventory page.
- features/vendors: vendors page.
- features/customers: customers page.
- layout: authenticated application layout and navigation.
Frontend request flow
1. The user submits tenant code, username and password on the login page.
2. Angular calls POST /api/v1/auth/login.
3. The access token is stored in browser sessionStorage.
4. Angular calls GET /api/v1/auth/me to load the authenticated user's profile.
5. The HTTP interceptor attaches the Bearer token to protected API requests.
6. The authentication guard protects the application routes.
7. The role guard checks the role allowed by route metadata.
8. The layout displays only the navigation items allowed for the loaded role.
9. Feature services call the corresponding FastAPI endpoints.
10. The backend performs the actual authentication, permission and tenant checks.
Local development proxy
frontend/proxy.conf.json forwards requests beginning with /api to http://127.0.0.1:8000. This avoids requiring browser-side cross-origin configuration for the local Angular development workflow.

This development proxy is not a production reverse-proxy or deployment architecture.
Authorization boundary
Frontend route guards and hidden navigation items improve the user experience but are not security controls by themselves. A user can attempt to call an API directly. Therefore, the FastAPI backend must continue enforcing permissions and tenant-scoped access for every protected operation.

The browser does not determine the tenant ID used for business-data access.
Phase 5 scope boundary
The implemented frontend provides read-oriented ERP pages and dashboard views using the existing backend APIs. It does not introduce new backend business endpoints, order creation workflows, an AI chat interface or production Spring Boot integration.

The AI assistant remains planned for a later phase.
