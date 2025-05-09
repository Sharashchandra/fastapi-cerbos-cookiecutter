import asyncio
from datetime import datetime, timezone

from src.core.constants import UserRoles
from src.core.security.passwords import Password
from src.database.session import AsyncSessionLocal
from src.users.models import User


async def create_normal_user():
    async with AsyncSessionLocal() as session:
        user = User(
            email="user@admin.com",
            password=Password.get_hashed_password("admin"),
            full_name="User",
            is_active=True,
            is_mfa_enabled=False,
            email_verified=True,
            last_login=datetime.now(timezone.utc),
            assigned_roles=[UserRoles.USER],
        )
        session.add(user)
        await session.commit()


if __name__ == "__main__":
    asyncio.run(create_normal_user())
