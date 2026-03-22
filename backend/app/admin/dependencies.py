from fastapi import Depends

from app.auth.dependencies import get_current_user
from app.auth.roles import require_role
from app.models.user import User, UserRole


def get_admin_user(user: User = Depends(require_role(UserRole.admin))) -> User:
    # Delegates role check to `require_role`.
    return user

