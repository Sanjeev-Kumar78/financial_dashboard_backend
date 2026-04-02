from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.security import decode_access_token
from app.core.exceptions import UnauthorizedException, ForbiddenException
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    payload = decode_access_token(token)
    user_id = payload.get("sub")

    if not user_id:
        raise UnauthorizedException("Invalid or expired token")

    user = db.query(User).filter(User.id == int(user_id), User.is_active == True).first()

    if not user:
        # Either the user was deleted or deactivated after the token was issued
        raise UnauthorizedException("User not found or account deactivated")

    return user

def require_role(*allowed_roles: str):
    # This is a factory, not a regular dependency.
    # You call it with the allowed roles and it RETURNS a dependency function.
    #
    # Usage on a route:
    #   dependencies=[Depends(require_role("admin", "analyst"))]
    #
    # This keeps authorization declarative  you can see who's allowed
    # just by reading the route definition, without digging into middleware.
    def _check(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise ForbiddenException(
                f"Role '{current_user.role}' is not permitted to perform this action"
            )
        return current_user
    return _check
