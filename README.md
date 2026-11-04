# AI-Powered ERP Assistant

A multi-tenant AI-powered ERP assistant built using Angular,
FastAPI, MySQL and Ollama.

## Technology Stack

- Frontend: Angular 21
- Backend: FastAPI and Python
- Database: MySQL 8
- ORM: SQLAlchemy 2
- Migrations: Alembic
- AI Model Server: Ollama
- LLM: qwen2.5:7b-instruct
- Testing: Pytest
- Containerization: Docker Compose

## Project Structure

```text
AI-powered ERP Assistant/
├── backend/
│   ├── alembic/
│   ├── app/
│   │   ├── ai/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── schemas/
│   │   ├── security/
│   │   └── services/
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── database/
├── docs/
├── frontend/
├── scripts/
├── .env.example
├── docker-compose.yml
└── README.md