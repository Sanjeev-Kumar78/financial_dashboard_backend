from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import hash_password, verify_password, create_access_token
from app.core.exceptions import BadRequestException, UnauthorizedException

def register_user(db: Session, payload: UserCreate) -> User:
    # Check for duplicate emails before trying to insert.
    # This gives a clean error instead of a DB constraint violation.
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise BadRequestException("An account with this email already exists")

    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        # New users start as viewers  an admin must explicitly elevate their role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def login_user(db: Session, email: str, password: str) -> str:
    user = db.query(User).filter(User.email == email).first()

    # Intentionally vague error  don't reveal whether the email exists
    if not user or not verify_password(password, user.hashed_password):
        raise UnauthorizedException("Invalid email or password")

    if not user.is_active:
        raise UnauthorizedException("This account has been deactivated")

    return create_access_token(user_id=user.id, role=user.role)
