from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.dependencies import require_role, get_current_user
from app.models.user import User
from app.services import dashboard_service
from datetime import date

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

# Viewers can see the dashboard  they just can't create or modify records
_read_access = Depends(require_role("admin", "analyst", "viewer"))

@router.get("/summary", dependencies=[_read_access])
def summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return dashboard_service.get_summary(db, current_user)

@router.get("/by-category", dependencies=[_read_access])
def by_category(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return dashboard_service.get_by_category(db, current_user)

@router.get("/trends", dependencies=[_read_access])
def trends(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    year: int = Query(default=date.today().year, ge=2000, le=2100),
):
    return dashboard_service.get_monthly_trends(db, current_user, year)

@router.get("/recent", dependencies=[_read_access])
def recent(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(default=10, ge=1, le=50),
):
    return dashboard_service.get_recent(db, current_user, limit)
