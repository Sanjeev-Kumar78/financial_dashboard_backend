from datetime import date as DateType
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from app.models.transaction import TransactionType, CategoryEnum


class TransactionCreate(BaseModel):
    amount: Decimal = Field(..., gt=0, examples=["2500.00"])
    type: TransactionType = Field(..., examples=["income"])
    category: CategoryEnum = Field(..., examples=["salary"])
    date: DateType = Field(..., examples=["2024-06-15"])
    notes: Optional[str] = Field(None, examples=["Monthly salary for June"])

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Amount must be greater than zero")
        return v

    @field_validator("date")
    @classmethod
    def date_cannot_be_future(cls, v):
        import datetime
        if v > datetime.date.today():
            raise ValueError("Transaction date cannot be in the future")
        return v


class TransactionUpdate(BaseModel):
    amount: Optional[Decimal] = Field(None, gt=0, examples=["3000.00"])
    type: Optional[TransactionType] = Field(None, examples=["expense"])
    category: Optional[CategoryEnum] = Field(None, examples=["food"])
    date: Optional[DateType] = Field(None, examples=["2024-07-01"])
    notes: Optional[str] = Field(None, examples=["Adjusted amount"])


class TransactionResponse(BaseModel):
    id: int = Field(..., examples=[1])
    amount: Decimal = Field(..., examples=["2500.00"])
    type: TransactionType = Field(..., examples=["income"])
    category: CategoryEnum = Field(..., examples=["salary"])
    date: DateType = Field(..., examples=["2024-06-15"])
    notes: Optional[str] = Field(None, examples=["Monthly salary for June"])
    user_id: int = Field(..., examples=[1])

    model_config = {"from_attributes": True}


class PagedTransactionResponse(BaseModel):
    items: List[TransactionResponse]
    total: int = Field(..., examples=[42])
    page: int = Field(..., examples=[1])
    page_size: int = Field(..., examples=[20])
    pages: int = Field(..., examples=[3])
