from typing import AsyncGenerator

from src.database.session import AsyncSessionLocal


async def get_db() -> AsyncGenerator:
    """
    Returns an async generator object that provides an asynchronous database session.
    """
    async with AsyncSessionLocal() as session:
        yield session
