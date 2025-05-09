from cerbos.engine.v1 import engine_pb2
from cerbos.sdk.grpc.client import AsyncCerbosClient
from fastapi import Depends, HTTPException, status
from google.protobuf.struct_pb2 import Value

from src.core.config import config
from src.core.constants import ResourceActions
from src.users.dependencies import get_current_user
from src.users.models import User


class PermissionChecker:
    def __init__(self, action: ResourceActions, resource_kind: str):
        self.action = action
        self.resource_kind = resource_kind

    def get_principal(self, user: User) -> engine_pb2.Principal:
        return engine_pb2.Principal(
            id=str(user.id),
            roles=user.assigned_roles,
            attr={
                "full_name": Value(string_value=user.full_name) if user.full_name else Value(string_value=""),
                "email": Value(string_value=user.email),
                "is_active": Value(bool_value=user.is_active),
                "is_mfa_enabled": Value(bool_value=user.is_mfa_enabled),
                "email_verified": Value(bool_value=user.email_verified),
                "is_blocked": Value(bool_value=user.is_blocked),
            },
        )

    def get_resource(self, user: User) -> engine_pb2.Resource:
        return engine_pb2.Resource(id=f"{self.resource_kind}_{str(user.id)}", kind=self.resource_kind)

    async def __call__(self, user: User = Depends(get_current_user)) -> None:
        principal = self.get_principal(user=user)
        resource = self.get_resource(user=user)

        async with AsyncCerbosClient(config.CERBOS_URL) as client:
            action_allowed = await client.is_allowed(
                action=self.action.value,
                principal=principal,
                resource=resource,
            )
            if not action_allowed:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You are not authorized to perform this action.",
                )
