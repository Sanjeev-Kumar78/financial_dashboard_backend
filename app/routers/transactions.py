from datetime import date as DateType
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.dependencies import require_role, get_current_user
from app.models.transaction import TransactionType, CategoryEnum
from app.models.user import User
from app.schemas.transaction import TransactionCreate, TransactionUpdate, TransactionResponse, PagedTransactionResponse
from app.services import transaction_service

router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.post("/", response_model=TransactionResponse, status_code=201,
             dependencies=[Depends(require_role("admin", "analyst"))])
def create(payload: TransactionCreate, db: Session = Depends(get_db),
           current_user: User = Depends(get_current_user)):
    return transaction_service.create_transaction(db, payload, current_user)

@router.get("/", response_model=PagedTransactionResponse,
            dependencies=[Depends(require_role("admin", "analyst", "viewer"))])
def list_all(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    type: Optional[TransactionType] = Query(None),
    category: Optional[CategoryEnum] = Query(None),
    date_from: Optional[DateType] = Query(None),
    date_to: Optional[DateType] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    return transaction_service.list_transactions(
        db, current_user, type, category, date_from, date_to, page, page_size
    )

@router.get("/{txn_id}", response_model=TransactionResponse,
            dependencies=[Depends(require_role("admin", "analyst", "viewer"))])
def get_one(txn_id: int, db: Session = Depends(get_db),
            current_user: User = Depends(get_current_user)):
    return transaction_service.get_transaction(db, txn_id, current_user)

@router.patch("/{txn_id}", response_model=TransactionResponse,
              dependencies=[Depends(require_role("admin", "analyst"))])
def update(txn_id: int, payload: TransactionUpdate, db: Session = Depends(get_db),
           current_user: User = Depends(get_current_user)):
    return transaction_service.update_transaction(db, txn_id, payload, current_user)

@router.delete("/{txn_id}", status_code=204,
               dependencies=[Depends(require_role("admin"))])
def delete(txn_id: int, db: Session = Depends(get_db),
           current_user: User = Depends(get_current_user)):
    transaction_service.delete_transaction(db, txn_id, current_user)
