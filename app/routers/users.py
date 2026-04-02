from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.dependencies import require_role
from app.schemas.user import UserResponse, UpdateRoleRequest, UpdateStatusRequest
from app.models.user import User
from app.services import user_service

# All routes here are admin-only  user management is a privileged operation
router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/", response_model=list[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    _: None = Depends(require_role("admin")),
):
    return user_service.get_all_users(db)

@router.patch("/{user_id}/role", response_model=UserResponse)
def update_role(
    user_id: int,
    payload: UpdateRoleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    return user_service.update_user_role(db, user_id, payload.role, current_user.id)

@router.patch("/{user_id}/status", response_model=UserResponse)
def update_status(
    user_id: int,
    payload: UpdateStatusRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    return user_service.update_user_status(db, user_id, payload.is_active, current_user.id)
