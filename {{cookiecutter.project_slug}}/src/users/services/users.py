from src.users.models import User


class UserService:
    @classmethod
    def get_user_detail(cls, user: User) -> dict:
        return user.json(exclude={"password"})
