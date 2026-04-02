def test_viewer_cannot_create_transaction(client):
    # Register and log in as a viewer
    client.post("/auth/register", json={"email": "viewer@test.com", "password": "password123"})
    login = client.post("/auth/login", json={"email": "viewer@test.com", "password": "password123"})
    token = login.json()["access_token"]

    # Attempt to create a transaction  viewers are not allowed
    response = client.post(
        "/transactions/",
        json={"amount": "100.00", "type": "income", "category": "salary",
              "date": "2024-01-15"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
    assert response.json()["error"] == "FORBIDDEN"
