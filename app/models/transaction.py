import enum
from datetime import date as DateType
from decimal import Decimal
from typing import Optional
from sqlalchemy import String, Numeric, Date, Boolean, ForeignKey, Text, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin

class TransactionType(str, enum.Enum):
    income  = "income"
    expense = "expense"

class CategoryEnum(str, enum.Enum):
    # Fixed enum keeps the DB consistent and makes aggregation queries simpler.
    # Trade-off: adding a new category requires a code change + migration.
    # This is acceptable for a finance system where categories should be controlled.
    salary      = "salary"
    freelance   = "freelance"
    investment  = "investment"
    food        = "food"
    transport   = "transport"
    utilities   = "utilities"
    healthcare  = "healthcare"
    education   = "education"
    rent        = "rent"
    other       = "other"

class Transaction(Base, TimestampMixin):
    __tablename__ = "transactions"

    id:          Mapped[int]             = mapped_column(primary_key=True)
    amount:      Mapped[Decimal]         = mapped_column(Numeric(12, 2))
    type:        Mapped[TransactionType] = mapped_column(SAEnum(TransactionType))
    category:    Mapped[CategoryEnum]    = mapped_column(SAEnum(CategoryEnum))
    date:        Mapped[DateType]        = mapped_column(Date)
    notes:       Mapped[Optional[str]]   = mapped_column(Text, nullable=True)
    is_deleted:  Mapped[bool]            = mapped_column(Boolean, default=False)
    # Soft delete  we never permanently remove financial records.
    # is_deleted=True hides the record from all queries without destroying history.

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user = relationship("User")
