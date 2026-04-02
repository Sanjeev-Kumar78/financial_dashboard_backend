from datetime import date as DateType
from decimal import Decimal
from typing import Optional
from sqlalchemy.orm import Session
from app.models.transaction import Transaction, TransactionType, CategoryEnum
from app.models.user import User, UserRole
from app.schemas.transaction import TransactionCreate, TransactionUpdate, PagedTransactionResponse
from app.core.exceptions import NotFoundException, ForbiddenException

def create_transaction(db: Session, payload: TransactionCreate, current_user: User) -> Transaction:
    txn = Transaction(**payload.model_dump(), user_id=current_user.id)
    db.add(txn)
    db.commit()
    db.refresh(txn)
    return txn

def list_transactions(
    db: Session,
    current_user: User,
    type: Optional[TransactionType] = None,
    category: Optional[CategoryEnum] = None,
    date_from: Optional[DateType] = None,
    date_to: Optional[DateType] = None,
    page: int = 1,
    page_size: int = 20,
) -> PagedTransactionResponse:

    # Start from a base query that already excludes soft-deleted records.
    # Every filter below narrows this  we never accidentally surface deleted data.
    query = db.query(Transaction).filter(Transaction.is_deleted == False)

    # Row-level access control  separate from route-level RBAC.
    # Admins see everything. Everyone else only sees their own transactions.
    if current_user.role != UserRole.admin:
        query = query.filter(Transaction.user_id == current_user.id)

    # Each filter is optional  only applied when the caller passed a value
    if type:
        query = query.filter(Transaction.type == type)
    if category:
        query = query.filter(Transaction.category == category)
    if date_from:
        query = query.filter(Transaction.date >= date_from)
    if date_to:
        query = query.filter(Transaction.date <= date_to)

    # Count before paginating  we need the total for the pagination envelope
    total = query.count()

    records = (
        query.order_by(Transaction.date.desc())
             .offset((page - 1) * page_size)
             .limit(page_size)
             .all()
    )

    return PagedTransactionResponse(
        items=records,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )

def get_transaction(db: Session, txn_id: int, current_user: User) -> Transaction:
    txn = db.query(Transaction).filter(
        Transaction.id == txn_id,
        Transaction.is_deleted == False,
    ).first()

    if not txn:
        raise NotFoundException(f"Transaction {txn_id} not found")

    # Non-admins can only access their own records
    if current_user.role != UserRole.admin and txn.user_id != current_user.id:
        raise ForbiddenException("You don't have access to this transaction")

    return txn

def update_transaction(db: Session, txn_id: int, payload: TransactionUpdate, current_user: User) -> Transaction:
    txn = get_transaction(db, txn_id, current_user)

    # Mass assignment protection: ignore immutables
    for field, value in payload.model_dump(exclude_unset=True).items():
        if field not in ['id', 'user_id', 'created_at', 'updated_at']:
            setattr(txn, field, value)

    db.commit()
    db.refresh(txn)
    return txn

def delete_transaction(db: Session, txn_id: int, current_user: User) -> None:
    txn = get_transaction(db, txn_id, current_user)
    # Soft delete  the record stays in the DB for audit purposes
    txn.is_deleted = True
    db.commit()
