# AI-Powered ERP Assistant – Architecture

## 1. Project Overview

The AI-Powered ERP Assistant is a multi-tenant AI application designed
to provide business insights and assistance using ERP data.

The existing ERP platform uses Java Spring Boot, MySQL and Angular.
This project implements an independent FastAPI-based AI service that
can integrate with the existing ERP through REST APIs.

## 2. Technology Stack

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

### AI
- Ollama
- qwen2.5:7b-instruct
- Controlled tool calling
- Pydantic-based output validation

### Infrastructure
- Docker
- Docker Compose
- Pytest

## 3. High-Level Architecture

```text
                Angular Frontend
                       |
                       | REST API
                       v
               FastAPI Backend
                       |
          +------------+------------+
          |            |            |
          v            v            v
      Security      Services    AI Assistant
      and RBAC      Layer           |
          |            |            v
          |            |          Ollama
          |            |
          +------------+
                       |
                       v
                  Repositories
                       |
                       v
                   MySQL 8