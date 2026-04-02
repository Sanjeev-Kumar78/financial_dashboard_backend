from datetime import date as DateType
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field


class Summary(BaseModel):
    total_income: Decimal = Field(..., examples=["15000.00"])
    total_expense: Decimal = Field(..., examples=["8500.00"])
    net_balance: Decimal = Field(..., examples=["6500.00"])


class CategoryTotal(BaseModel):
    category: str = Field(..., examples=["salary"])
    total: Decimal = Field(..., examples=["10000.00"])
    count: int = Field(..., examples=[4])


class MonthlyTrend(BaseModel):
    month: str = Field(..., examples=["2024-06"])
    income: Decimal = Field(..., examples=["5000.00"])
    expense: Decimal = Field(..., examples=["2300.00"])
    net: Decimal = Field(..., examples=["2700.00"])


class RecentTransaction(BaseModel):
    id: int = Field(..., examples=[5])
    amount: Decimal = Field(..., examples=["120.00"])
    type: str = Field(..., examples=["expense"])
    category: str = Field(..., examples=["food"])
    date: DateType = Field(..., examples=["2024-06-20"])
    notes: Optional[str] = Field(None, examples=["Team lunch"])
