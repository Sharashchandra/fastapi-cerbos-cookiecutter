# FastAPI-Cerbos Cookiecutter

A production-ready FastAPI application template with Cerbos integration for fine-grained authorization.

## Features

- FastAPI framework for high-performance API development
- Cerbos integration for policy-based access control
- PostgreSQL database with SQLAlchemy ORM
- Redis for caching and task queue
- Alembic for database migrations
- JWT authentication with refresh tokens
- Docker and docker-compose setup for easy deployment
- Role-based access control (RBAC)
- Background task processing with RQ
- Pre-configured development environment

## Installation

### Prerequisites

- Python 3.13+
- uv
- cookiecutter
- Docker and docker-compose

### Install Cookiecutter

If you don't have cookiecutter installed, you can install it using uv:

```bash
pip install cookiecutter
```

### Generate Project

Generate a new project from this template:

```bash
cookiecutter gh:sharashchandra/fastapi-cerbos-cookiecutter
```

You'll be prompted to provide several values:

- `project_name`: Name of your project
- `project_slug`: Slug for your project (auto-generated from project_name)
- `author_name`: Your name
- `author_email`: Your email
- `description`: Short description of your project
