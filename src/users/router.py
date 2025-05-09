from fastapi import APIRouter, Depends, status

from src.core.constants import ResourceActions
from src.core.permissions.dependencies import PermissionChecker
from src.users.dependencies import get_current_user
from src.users.models import User
from src.users.services.users import UserService

user_router = APIRouter(prefix="/users", tags=["Users"])


@user_router.get(
    "/details/",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionChecker(action=ResourceActions.GET, resource_kind="users"))],
)
def get_user_detail(user: User = Depends(get_current_user)) -> dict:
    return UserService.get_user_detail(user=user)
