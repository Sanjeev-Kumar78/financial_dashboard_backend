from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.core.exceptions import NotFoundException, BadRequestException

def get_all_users(db: Session) -> list[User]:
    # Admin-only. Returns all users including inactive ones
    # so admins can see and reactivate deactivated accounts.
    return db.query(User).all()

def update_user_role(db: Session, user_id: int, new_role: UserRole, current_user_id: int) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFoundException(f"No user found with id {user_id}")
    
    if user.id == current_user_id and new_role != UserRole.admin:
        raise BadRequestException("Admins cannot strip their own admin privileges")
        
    user.role = new_role
    db.commit()
    db.refresh(user)
    return user

def update_user_status(db: Session, user_id: int, is_active: bool, current_user_id: int) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFoundException(f"No user found with id {user_id}")
        
    if user.id == current_user_id and is_active is False:
        raise BadRequestException("Admins cannot deactivate their own account")
        
    user.is_active = is_active
    db.commit()
    db.refresh(user)
    return user
