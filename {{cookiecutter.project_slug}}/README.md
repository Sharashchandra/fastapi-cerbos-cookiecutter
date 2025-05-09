# {{cookiecutter.project_name}}

{{cookiecutter.description}}

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

## Getting Started

### Prerequisites

- Python 3.13+
- Docker and docker-compose

### Setup

1. Copy the example environment file to create your `.env` file:

```bash
cp env.example .env
```

2. Update the `.env` file with your specific values:
   - Generate a secure random string for `JWT_SECRET_KEY`:
     ```python
     import secrets
     print(secrets.token_hex(32))
     # Output: 3d6f45a5fc12445dbac2f59c3b6c7cb1d3c11316f7e4f5cad6a53449a8d02fd8
     ```
   - Update SMTP settings if you need email functionality
   - Modify database credentials if needed

### Configure Authorization Policies

1. Customize the user roles and resource actions in `src/core/constants.py` according to your application requirements:

```python
class UserRoles(str, Enum):
    # Add or modify roles as needed
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"
    USER = "user"

class ResourceActions(str, Enum):
    # Add or modify actions as needed
    LIST = "list"
    GET = "get"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
```

2. Generate Cerbos policy files:
   - Go to [play.cerbos.dev](https://play.cerbos.dev) to create your policy files
   - Define policies based on your roles and actions
   - Save the generated YAML files to the `authz/policies` folder in your project

## Running the Application

1. Update the packages to the latest version in `pyproject.toml`

2. Generate the lock file using uv:

```bash
uv lock
```

3. Start the application using docker-compose:

```bash
docker-compose up -d
```

This will start the following services:
- FastAPI application (accessible at http://localhost:8000)
- PostgreSQL database
- Redis
- Background worker
- Cerbos policy decision point

API documentation is available at:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

### Database Migrations

To create and apply database migrations:

1. Access the application container:
```bash
docker-compose exec app bash
```

2. Generate a new migration:
```bash
alembic revision --autogenerate -m "your migration message"
```

3. Apply the migration:
```bash
alembic upgrade head
```

### Background Jobs with RQ

This project uses [RQ (Redis Queue)](https://python-rq.org/) for processing background jobs. A dashboard to monitor and manage these jobs is available at:

```
http://localhost:8000/rq
```

You can use this dashboard to:
- Monitor active, queued, and finished jobs
- View job details and results
- Requeue failed jobs
- Clear queues

To create and enqueue a background job:

```python
from src.core.helpers.rq import queue

def my_background_task(param1, param2):
    # Task logic here
    return result

# Enqueue the job
job = queue.enqueue(my_background_task, param1, param2)
```

## Development Guidelines

### Project Structure

```
.
├── alembic/              # Database migration scripts
├── authz/                # Cerbos authorization policies
├── docker/               # Docker configuration files
├── scripts/              # Utility scripts
├── src/                  # Application source code
│   ├── authentication/   # Authentication logic
│   ├── core/             # Core functionality
│   ├── database/         # Database models and configuration
│   ├── notifications/    # Notification services
│   ├── users/            # User management
│   └── main.py           # Application entry point
├── .env                  # Environment variables
├── docker-compose.yaml   # Docker compose configuration
└── pyproject.toml        # Python dependencies
```

### Adding New Models

When creating new models, make sure to import them in `src/database/base.py` to enable Alembic to auto-generate migrations:

```python
# Import all the models, so that Base has them before being imported by Alembic
from src.database.base_class import Base  # isort:skip # noqa: F401

from src.users.models import User  # noqa: F401
# Import your new models here
from src.your_module.models import YourModel  # noqa: F401
```

### Adding New Routers

When adding new API routers:

1. Create your router module
2. Import and include it in `src/core/routers/api.py`:

```python
from src.your_module.router import your_router

# For endpoints that require authentication
router_with_auth.include_router(your_router)

# OR for endpoints that don't require authentication
router_without_auth.include_router(your_router)
```

## Deployment

This application is containerized and can be deployed to any environment that supports Docker containers. The provided docker-compose.yaml file is suitable for development and testing environments.

For production deployments, consider:

1. Using a managed database service instead of the containerized PostgreSQL
2. Setting up proper SSL/TLS termination
3. Implementing a CI/CD pipeline for automated testing and deployment
4. Using container orchestration like Kubernetes for high availability

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.

## Authors

- {{cookiecutter.author_name}} - {{cookiecutter.author_email}}