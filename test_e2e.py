"""End-to-end test script for Finance Advisor API"""
import httpx
import sys

BASE = "http://127.0.0.1:8000/api/v1"
passed = 0
failed = 0

def test(name, status_code, expected=None):
    global passed, failed
    if expected is None:
        expected = [200, 201, 204]
    if status_code in expected:
        passed += 1
        print(f"  PASS: {name} ({status_code})")
    else:
        failed += 1
        print(f"  FAIL: {name} (got {status_code}, expected {expected})")

# 1. Register
print("\n=== REGISTER ===")
r = httpx.post(f"{BASE}/auth/register", json={
    "email": "e2e@test.com", "full_name": "E2E User", "password": "Test1234!"
})
test("Register", r.status_code, [201, 409])
if r.status_code == 201:
    data = r.json()
    token = data["access_token"]
    refresh = data["refresh_token"]
elif r.status_code == 409:
    r = httpx.post(f"{BASE}/auth/login", json={"email": "e2e@test.com", "password": "Test1234!"})
    data = r.json()
    token = data["access_token"]
    refresh = data["refresh_token"]
else:
    print(f"FATAL: Cannot proceed - {r.text}")
    sys.exit(1)

headers = {"Authorization": f"Bearer {token}"}

# 2. Login
print("\n=== LOGIN ===")
r = httpx.post(f"{BASE}/auth/login", json={"email": "e2e@test.com", "password": "Test1234!"})
test("Login", r.status_code)
data = r.json()
token = data["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 3. Get current user
print("\n=== USERS ===")
r = httpx.get(f"{BASE}/users/me", headers=headers)
test("GET /users/me", r.status_code)
if r.status_code == 200:
    print(f"    User: {r.json()['email']}")

# 4. Update profile
r = httpx.patch(f"{BASE}/users/me", headers=headers, json={"full_name": "E2E Updated"})
test("PATCH /users/me", r.status_code)

# 5. Incomes
print("\n=== INCOMES ===")
r = httpx.post(f"{BASE}/incomes", headers=headers, json={
    "source": "Salary", "category": "Salary", "amount": 5000,
    "frequency": "Monthly", "received_date": "2026-08-01"
})
test("Create Income", r.status_code)
if r.status_code == 201:
    income_id = r.json()["id"]
    r = httpx.get(f"{BASE}/incomes", headers=headers)
    test("List Incomes", r.status_code)
    r = httpx.get(f"{BASE}/incomes/{income_id}", headers=headers)
    test("Get Income", r.status_code)
    r = httpx.put(f"{BASE}/incomes/{income_id}", headers=headers, json={"amount": 5500})
    test("Update Income", r.status_code)
    r = httpx.delete(f"{BASE}/incomes/{income_id}", headers=headers)
    test("Delete Income", r.status_code)

# 6. Expenses
print("\n=== EXPENSES ===")
r = httpx.post(f"{BASE}/expenses", headers=headers, json={
    "category": "Food", "amount": 200, "spent_at": "2026-08-01"
})
test("Create Expense", r.status_code)
if r.status_code == 201:
    expense_id = r.json()["id"]
    r = httpx.get(f"{BASE}/expenses", headers=headers)
    test("List Expenses", r.status_code)
    r = httpx.get(f"{BASE}/expenses/{expense_id}", headers=headers)
    test("Get Expense", r.status_code)
    r = httpx.put(f"{BASE}/expenses/{expense_id}", headers=headers, json={"amount": 250})
    test("Update Expense", r.status_code)
    r = httpx.delete(f"{BASE}/expenses/{expense_id}", headers=headers)
    test("Delete Expense", r.status_code)

# 7. Budgets
print("\n=== BUDGETS ===")
r = httpx.post(f"{BASE}/budgets", headers=headers, json={
    "month": 8, "year": 2026, "category": "Food", "budget_amount": 500
})
test("Create Budget", r.status_code)
if r.status_code == 201:
    budget_id = r.json()["id"]
    r = httpx.get(f"{BASE}/budgets", headers=headers)
    test("List Budgets", r.status_code)
    r = httpx.get(f"{BASE}/budgets/{budget_id}", headers=headers)
    test("Get Budget", r.status_code)
    r = httpx.put(f"{BASE}/budgets/{budget_id}", headers=headers, json={"budget_amount": 600})
    test("Update Budget", r.status_code)
    r = httpx.delete(f"{BASE}/budgets/{budget_id}", headers=headers)
    test("Delete Budget", r.status_code)

# 8. Finance Summary
print("\n=== FINANCE ===")
r = httpx.get(f"{BASE}/finance/summary", headers=headers)
test("Finance Summary", r.status_code)
if r.status_code == 200:
    print(f"    Summary: {r.json()}")

# 9. Refresh Token
print("\n=== TOKEN REFRESH ===")
r = httpx.post(f"{BASE}/auth/refresh", json={"refresh_token": refresh})
test("Refresh Token", r.status_code)

# 10. System
print("\n=== SYSTEM ===")
r = httpx.get("http://127.0.0.1:8000/version")
test("GET /version", r.status_code)

# 11. AI Endpoints
print("\n=== AI ENDPOINTS ===")
r = httpx.post(f"{BASE}/ai/financial-health", headers=headers)
test("Financial Health", r.status_code)
if r.status_code == 200:
    print(f"    Score: {r.json()['overall_score']}")

r = httpx.post(f"{BASE}/ai/recommendations", headers=headers)
test("Recommendations", r.status_code)
if r.status_code == 200:
    print(f"    Tips: {len(r.json()['spending_tips'])}")

r = httpx.post(f"{BASE}/ai/chat", headers=headers, json={"message": "How can I save money?"})
test("AI Chat", r.status_code)

r = httpx.post(f"{BASE}/ai/budget-optimizer", headers=headers)
test("Budget Optimizer", r.status_code)

r = httpx.post(f"{BASE}/ai/spending-forecast", headers=headers)
test("Spending Forecast", r.status_code)

r = httpx.post(f"{BASE}/ai/investment-advisor", headers=headers)
test("Investment Advisor", r.status_code)

r = httpx.post(f"{BASE}/ai/portfolio", headers=headers)
test("Portfolio", r.status_code)

r = httpx.post(f"{BASE}/ai/stock-predict", headers=headers, json={"symbol": "AAPL"})
test("Stock Predict", r.status_code)

r = httpx.post(f"{BASE}/ai/house-price-predict", headers=headers, json={"area": 1500, "bedrooms": 3, "bathrooms": 2, "location": "New York"})
test("House Price Predict", r.status_code)

# Summary
print(f"\n{'='*40}")
print(f"TESTS: {passed} passed, {failed} failed, {passed+failed} total")
if failed == 0:
    print("ALL TESTS PASSED!")
else:
    print(f"FAILURES: {failed}")
    sys.exit(1)
