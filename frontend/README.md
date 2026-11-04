# AI-Powered ERP Assistant — Frontend

Angular 21 frontend for the multi-tenant ERP Assistant. The frontend communicates with the FastAPI backend and displays authenticated ERP dashboard and business data.

## Requirements

- Node.js and npm.
- FastAPI backend running at `http://127.0.0.1:8000`.
- MySQL database and backend environment configured as described in the root README.

## Install dependencies

Run from this directory:

```bash
npm install
```

## Start the development server

```bash
npm start
```

Open `http://localhost:4200`.

The Angular development server uses `proxy.conf.json` to forward `/api` requests to `http://127.0.0.1:8000`.

Start the FastAPI backend separately. The frontend proxy does not start the backend or database.

## Authentication

The login page accepts:

- Tenant code
- Username
- Password

The frontend calls:

- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`

The access token is stored in browser `sessionStorage`. The HTTP interceptor attaches it to protected API requests using the Bearer authorization scheme.

## Available pages

- Dashboard
- Sales
- Purchases
- Inventory
- Vendors
- Customers

The visible navigation and route access are based on the role returned by the backend.

| Role | Visible pages |
|---|---|
| Administrator | Dashboard, Sales, Purchases, Inventory, Vendors, Customers |
| Sales Executive | Dashboard, Sales, Inventory, Customers |
| Purchase Executive | Dashboard, Purchases, Inventory, Vendors |
| Management | Dashboard, Sales, Purchases, Inventory, Vendors, Customers |

Frontend role checks are for navigation and user experience. Backend authorization and tenant isolation remain mandatory.

## Build

```bash
npx ng build
```

## Unit tests

Run tests once:

```bash
npx ng test --watch=false
```

## API integration

The frontend calls the existing FastAPI endpoints under `/api/v1`. The local proxy configuration is intended for development only. Production API routing and deployment configuration must be supplied by the deployment environment.

## Current scope

The frontend currently provides login, dashboard and read-oriented ERP pages with loading, error, empty-state, refresh and pagination handling.

The AI Assistant interface and workflow, write operations and production integration with the existing Spring Boot ERP are not included in this Phase 5 frontend scope.
