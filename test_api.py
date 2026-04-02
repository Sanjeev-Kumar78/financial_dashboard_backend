"""Quick integration test script  exercises all API endpoints."""
import httpx
import json
import sys

base = "http://127.0.0.1:8000"
passed = 0
failed = 0

def check(label, condition, detail=""):
    global passed, failed
    if condition:
        print(f"  PASS: {label}")
        passed += 1
    else:
        print(f"  FAIL: {label} -- {detail}")
        failed += 1

print("\n=== Phase 1: Health ===")
r = httpx.get(f"{base}/health")
check("GET /health -> 200", r.status_code == 200, r.text)

print("\n=== Phase 2: Auth ===")
r = httpx.post(f"{base}/auth/register", json={"email": "admin@test.com", "password": "admin123"})
check("POST /auth/register -> 201", r.status_code == 201, r.text)

r = httpx.post(f"{base}/auth/login", data={"username": "admin@test.com", "password": "admin123"})
check("POST /auth/login -> 200", r.status_code == 200, r.text)
token = r.json().get("access_token", "")
headers = {"Authorization": f"Bearer {token}"}

# Register a viewer
r = httpx.post(f"{base}/auth/register", json={"email": "viewer@test.com", "password": "viewer123"})
check("Register viewer -> 201", r.status_code == 201, r.text)
r = httpx.post(f"{base}/auth/login", data={"username": "viewer@test.com", "password": "viewer123"})
viewer_token = r.json().get("access_token", "")
viewer_headers = {"Authorization": f"Bearer {viewer_token}"}

print("\n=== Phase 2: RBAC -- viewer cannot create transaction ===")
r = httpx.post(f"{base}/transactions/", json={
    "amount": "50.00", "type": "income", "category": "salary", "date": "2024-01-01"
}, headers=viewer_headers)
check("Viewer POST /transactions/ -> 403", r.status_code == 403, r.text)

print("\n=== Phase 3: Read endpoints (as viewer) ===")
r = httpx.get(f"{base}/transactions/", headers=viewer_headers)
check("Viewer GET /transactions/ -> 200", r.status_code == 200, r.text)

print("\n=== Phase 4: Dashboard (as viewer) ===")
r = httpx.get(f"{base}/dashboard/summary", headers=viewer_headers)
check("Viewer GET /dashboard/summary -> 200", r.status_code == 200, r.text)

r = httpx.get(f"{base}/dashboard/by-category", headers=viewer_headers)
check("Viewer GET /dashboard/by-category -> 200", r.status_code == 200, r.text)

r = httpx.get(f"{base}/dashboard/trends?year=2024", headers=viewer_headers)
check("Viewer GET /dashboard/trends -> 200", r.status_code == 200, r.text)

r = httpx.get(f"{base}/dashboard/recent", headers=viewer_headers)
check("Viewer GET /dashboard/recent -> 200", r.status_code == 200, r.text)

print(f"\n{'='*40}")
print(f"Results: {passed} passed, {failed} failed")
if failed > 0:
    sys.exit(1)
