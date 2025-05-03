from src.database.crud_base import CRUDBase
from src.users.models import BlacklistedToken, MFAAttempt, User


class CRUDUser(CRUDBase): ...


crud_user = CRUDUser(model=User)


class CRUDMFAAttempt(CRUDBase): ...


crud_mfa_attempt = CRUDMFAAttempt(model=MFAAttempt)


class CRUDBlacklistedToken(CRUDBase): ...


crud_blacklisted_token = CRUDBlacklistedToken(model=BlacklistedToken)
