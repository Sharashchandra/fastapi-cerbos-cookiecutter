# Import all the models, so that Base has them before being imported by Alembic
from src.database.base_class import Base  # isort:skip # noqa: F401

from src.users.models import BlacklistedToken, MFAAttempt, User  # noqa: F401
