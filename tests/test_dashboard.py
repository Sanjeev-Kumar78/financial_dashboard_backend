from app.models.transaction import Transaction, TransactionType, CategoryEnum
from app.core.security import hash_password
from app.models.user import User, UserRole
from datetime import date

def test_dashboard_summary_totals_are_correct(client, db):
    # Create an admin user directly in the DB  bypasses the register endpoint
    admin = User(email="admin@test.com", hashed_password=hash_password("pass"),
                 role=UserRole.admin)
    db.add(admin)
    db.commit()
    db.refresh(admin)

    # Seed known transactions so we can assert exact totals
    db.add_all([
        Transaction(amount=1000, type=TransactionType.income,
                    category=CategoryEnum.salary, date=date(2024, 1, 10), user_id=admin.id),
        Transaction(amount=200, type=TransactionType.expense,
                    category=CategoryEnum.food, date=date(2024, 1, 15), user_id=admin.id),
        Transaction(amount=300, type=TransactionType.expense,
                    category=CategoryEnum.transport, date=date(2024, 1, 20), user_id=admin.id),
    ])
    db.commit()

    login = client.post("/auth/login", json={"email": "admin@test.com", "password": "pass"})
    token = login.json()["access_token"]

    response = client.get("/dashboard/summary",
                          headers={"Authorization": f"Bearer {token}"})

    data = response.json()
    assert response.status_code == 200
    assert float(data["total_income"])  == 1000.0
    assert float(data["total_expense"]) == 500.0
    assert float(data["net_balance"])   == 500.0
