from sqlalchemy.orm import Session
from sqlalchemy import func, case, extract
from app.models.transaction import Transaction, TransactionType
from app.models.user import User, UserRole
from app.schemas.dashboard import Summary, CategoryTotal, MonthlyTrend, RecentTransaction
from decimal import Decimal

def _base_query(db: Session, current_user: User):
    """Returns a base query pre-filtered for soft-deletes and user role."""
    query = db.query(Transaction).filter(Transaction.is_deleted == False)
    if current_user.role != UserRole.admin:
        query = query.filter(Transaction.user_id == current_user.id)
    return query

def get_summary(db: Session, current_user: User) -> Summary:
    query = _base_query(db, current_user)
    
    # Pure ORM aggregation — safely generates cross-dialect SQL
    # Equivalent to SUM(CASE WHEN type='income' THEN amount ELSE 0 END)
    income_expr = func.coalesce(
        func.sum(case((Transaction.type == TransactionType.income, Transaction.amount), else_=0)), 
        0
    )
    expense_expr = func.coalesce(
        func.sum(case((Transaction.type == TransactionType.expense, Transaction.amount), else_=0)), 
        0
    )
    
    result = query.with_entities(income_expr.label("total_income"), expense_expr.label("total_expense")).first()
    
    income = Decimal(str(result.total_income))
    expense = Decimal(str(result.total_expense))
    return Summary(total_income=income, total_expense=expense, net_balance=income - expense)


def get_by_category(db: Session, current_user: User) -> list[CategoryTotal]:
    query = _base_query(db, current_user)
    
    results = (
        query.with_entities(
            Transaction.category,
            func.sum(Transaction.amount).label("total"),
            func.count(Transaction.id).label("count")
        )
        .group_by(Transaction.category)
        .order_by(func.sum(Transaction.amount).desc())
        .all()
    )
    
    return [CategoryTotal(category=r.category, total=Decimal(str(r.total)), count=r.count) for r in results]


def get_monthly_trends(db: Session, current_user: User, year: int) -> list[MonthlyTrend]:
    query = _base_query(db, current_user)
    
    # Filter by requested year
    query = query.filter(extract('year', Transaction.date) == year)
    
    # Format month as string for cross-dialect bucketing
    # In sqlite strftime('%Y-%m') works, in Postgres we can use to_char(date, 'YYYY-MM')
    # But a robust native cross-dialect way is grouping by Year and Month separately, then formatting in Python
    results = (
        query.with_entities(
            extract('year', Transaction.date).label("year"),
            extract('month', Transaction.date).label("month"),
            func.coalesce(func.sum(case((Transaction.type == TransactionType.income, Transaction.amount), else_=0)), 0).label("income"),
            func.coalesce(func.sum(case((Transaction.type == TransactionType.expense, Transaction.amount), else_=0)), 0).label("expense"),
        )
        .group_by(extract('year', Transaction.date), extract('month', Transaction.date))
        .order_by(extract('year', Transaction.date), extract('month', Transaction.date))
        .all()
    )
    
    trends = []
    for r in results:
        # Cross-dialect safety: group by extracted year/month, then pad month to 'YYYY-MM'
        month_str = f"{int(r.year)}-{int(r.month):02d}"
        income = Decimal(str(r.income))
        expense = Decimal(str(r.expense))
        trends.append(MonthlyTrend(month=month_str, income=income, expense=expense, net=income - expense))
        
    return trends


def get_recent(db: Session, current_user: User, limit: int = 10) -> list[RecentTransaction]:
    query = _base_query(db, current_user)
    
    results = query.order_by(Transaction.date.desc(), Transaction.created_at.desc()).limit(limit).all()
    
    return [
        RecentTransaction(
            id=r.id,
            amount=r.amount,
            type=r.type.value,
            category=r.category.value,
            date=r.date,
            notes=r.notes
        ) for r in results
    ]
