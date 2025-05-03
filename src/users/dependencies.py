from fastapi import Depends
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.core.security.dependencies import verify_http_token
from src.database.dependencies import get_db
from src.users.crud import crud_user
from src.users.exceptions import UserNotFoundException
from src.users.models import User


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token_payload: dict = Depends(verify_http_token),
) -> User:
    user = await crud_user.get(db, id=token_payload["user_id"])
    if not user:
        raise UserNotFoundException()

    return user
