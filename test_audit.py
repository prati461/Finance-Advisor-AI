"""
Complete End-to-End Audit Script
Tests all backend endpoints and verifies functionality
"""
import urllib.request
import json
import sys
import time

BASE = "http://127.0.0.1:8000"
passed = 0
failed = 0
errors = []

def test(name, method, path, data=None, token=None, expected_status=200):
    global passed, failed
    url = f"{BASE}{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        body = json.dumps(data).encode() if data else b"{}" if method == "POST" else None
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        resp = urllib.request.urlopen(req)
        raw = resp.read()
        status = resp.status
        result = json.loads(raw) if raw else None
        if status == expected_status:
            passed += 1
            print(f"  ✅ {name} - Status {status}")
            return result
        else:
            failed += 1
            msg = f"  ❌ {name} - Expected {expected_status}, got {status}"
            print(msg)
            errors.append(msg)
            return None
    except urllib.error.HTTPError as e:
        status = e.code
        body = e.read().decode()
        if status == expected_status:
            passed += 1
            print(f"  ✅ {name} - Status {status} (expected error)")
            try:
                return json.loads(body) if body else None
            except:
                return body
        else:
            failed += 1
            msg = f"  ❌ {name} - Status {status}: {body[:200]}"
            print(msg)
            errors.append(msg)
            return None
    except Exception as e:
        failed += 1
        msg = f"  ❌ {name} - Exception: {e}"
        print(msg)
        errors.append(msg)
        return None

print("=" * 60)
print("PHASE 2: BACKEND VERIFICATION")
print("=" * 60)

# 1. Health & Version
print("\n--- System Endpoints ---")
test("Health Check", "GET", "/api/v1/health")
test("Version Check", "GET", "/api/v1/version")

# 2. Auth
print("\n--- Auth Endpoints ---")
import random
unique_id = str(random.randint(10000, 99999))
test_email = f"audit_{unique_id}@test.com"

# Register new user - returns 201
reg_data = test("Register User", "POST", "/api/v1/auth/register", 
                {"email": test_email, "password": "Test123!", "full_name": "Audit User"},
                expected_status=201)

# Login - returns 200
login_data = test("Login", "POST", "/api/v1/auth/login",
                  {"email": test_email, "password": "Test123!"},
                  expected_status=200)

if login_data and "access_token" in login_data:
    token = login_data["access_token"]
    print(f"  Token obtained: {token[:20]}...")
else:
    # Try existing user
    login_data = test("Login Existing", "POST", "/api/v1/auth/login",
                      {"email": "test@test.com", "password": "Test123!"},
                      expected_status=200)
    token = login_data["access_token"] if login_data else None

if not token:
    print("  ❌ Cannot proceed without authentication token")
    sys.exit(1)

# 3. User endpoints
print("\n--- User Endpoints ---")
test("Get Profile", "GET", "/api/v1/users/me", token=token)
# Change Password returns 204 (no content)
test("Change Password", "POST", "/api/v1/users/me/change-password",
     {"current_password": "Test123!", "new_password": "NewTest123!"}, token=token,
     expected_status=204)
# Change back
test("Change Password Back", "POST", "/api/v1/users/me/change-password",
     {"current_password": "NewTest123!", "new_password": "Test123!"}, token=token,
     expected_status=204)

# 4. CRUD Endpoints
print("\n--- Income Endpoints ---")
# Create returns 201
income = test("Create Income", "POST", "/api/v1/incomes",
              {"source": "Salary", "category": "Salary", "amount": 50000, 
               "frequency": "Monthly", "received_date": "2025-01-15", "description": "Monthly salary"},
              token=token, expected_status=201)
income_id = income["id"] if income else None

test("List Incomes", "GET", "/api/v1/incomes?page=1&page_size=10", token=token)
if income_id:
    test("Get Income", "GET", f"/api/v1/incomes/{income_id}", token=token)
    test("Update Income", "PUT", f"/api/v1/incomes/{income_id}",
         {"source": "Salary", "category": "Salary", "amount": 55000, 
          "frequency": "Monthly", "received_date": "2025-01-15", "description": "Updated salary"},
         token=token)
    test("Delete Income", "DELETE", f"/api/v1/incomes/{income_id}", token=token, expected_status=204)

print("\n--- Expense Endpoints ---")
# Create returns 201
expense = test("Create Expense", "POST", "/api/v1/expenses",
               {"category": "Food", "amount": 1500, "spent_at": "2025-01-15", 
                "description": "Groceries", "merchant": "Supermarket"},
               token=token, expected_status=201)
expense_id = expense["id"] if expense else None

test("List Expenses", "GET", "/api/v1/expenses?page=1&page_size=10", token=token)
if expense_id:
    test("Get Expense", "GET", f"/api/v1/expenses/{expense_id}", token=token)
    test("Update Expense", "PUT", f"/api/v1/expenses/{expense_id}",
         {"category": "Food", "amount": 2000, "spent_at": "2025-01-15", 
          "description": "Groceries", "merchant": "Supermarket"}, token=token)

print("\n--- Budget Endpoints ---")
# Create returns 201
budget = test("Create Budget", "POST", "/api/v1/budgets",
              {"month": 1, "year": 2025, "category": "Food", 
               "budget_amount": 20000, "alert_threshold_pct": 80},
              token=token, expected_status=201)
budget_id = budget["id"] if budget else None

test("List Budgets", "GET", "/api/v1/budgets?month=1&year=2025", token=token)
if budget_id:
    test("Get Budget", "GET", f"/api/v1/budgets/{budget_id}", token=token)

print("\n--- Finance Endpoints ---")
test("Monthly Summary", "GET", "/api/v1/finance/summary?month=1&year=2025", token=token)

# 5. AI Endpoints
print("\n--- AI Endpoints ---")
health = test("Financial Health", "POST", "/api/v1/ai/financial-health", token=token)
if health:
    print(f"    Score: {health.get('overall_score')}, Category: {health.get('category')}")
    print(f"    Components: {list(health.get('components', {}).keys())}")
    print(f"    Suggestions: {len(health.get('suggestions', []))}")

recs = test("Recommendations", "POST", "/api/v1/ai/recommendations", token=token)
if recs:
    print(f"    Goals: {len(recs.get('priority_goals', []))}")
    print(f"    Spending Tips: {len(recs.get('spending_tips', []))}")
    print(f"    Emergency Fund: {recs.get('emergency_fund', {}).get('status')}")

opt = test("Budget Optimizer", "POST", "/api/v1/ai/budget-optimizer", token=token)
if opt:
    print(f"    Optimizations: {len(opt.get('optimizations', []))}")
    print(f"    Potential Savings: {opt.get('potential_savings')}")

forecast = test("Spending Forecast", "POST", "/api/v1/ai/spending-forecast", token=token)
if forecast:
    print(f"    Next Income: {forecast.get('next_month_income')}")
    print(f"    Next Expense: {forecast.get('next_month_expense')}")
    print(f"    Confidence: {forecast.get('confidence_score')}")

inv = test("Investment Advisor", "POST", "/api/v1/ai/investment-advisor", token=token)
if inv:
    print(f"    Risk Profile: {inv.get('risk_profile')}")
    print(f"    Monthly Capacity: {inv.get('monthly_investment_capacity')}")
    print(f"    Allocation: {inv.get('allocation')}")

port = test("Portfolio", "POST", "/api/v1/ai/portfolio", token=token)
if port:
    print(f"    Risk: {port.get('risk_level')}")
    print(f"    Return: {port.get('expected_annual_return')}%")
    print(f"    Assets: {len(port.get('portfolio', []))}")

stock = test("Stock Predict", "POST", "/api/v1/ai/stock-predict",
             {"symbol": "AAPL"}, token=token)
if stock:
    print(f"    Symbol: {stock.get('symbol')}")
    print(f"    Tomorrow: {stock.get('tomorrow_price')}")
    print(f"    Trend: {stock.get('trend')}")
    print(f"    Confidence: {stock.get('confidence_score')}")

house = test("House Price", "POST", "/api/v1/ai/house-price-predict",
             {"area": 1500, "bedrooms": 3, "bathrooms": 2, "location": "Mumbai"}, token=token)
if house:
    print(f"    Price: {house.get('predicted_price')}")
    print(f"    Range: {house.get('price_range_low')} - {house.get('price_range_high')}")
    print(f"    Rating: {house.get('investment_rating')}")

fraud = test("Fraud Detection", "POST", "/api/v1/ai/fraud-detection", token=token)
if fraud:
    print(f"    Alerts: {len(fraud.get('alerts', []))}")
    print(f"    Analyzed: {fraud.get('total_analyzed')}")

chat = test("Chatbot", "POST", "/api/v1/ai/chat",
            {"message": "How can I save more money?"}, token=token)
if chat:
    print(f"    Response: {chat.get('response', '')[:80]}...")
    print(f"    Confidence: {chat.get('confidence')}")

analytics = test("Analytics", "POST", "/api/v1/ai/analytics",
                 {"period": "monthly"}, token=token)
if analytics:
    print(f"    Period: {analytics.get('period')}")
    print(f"    Income: {analytics.get('total_income')}")
    print(f"    Expense: {analytics.get('total_expense')}")

reports = test("Reports", "POST", "/api/v1/ai/reports",
               {"month": 1, "year": 2025, "format": "pdf"}, token=token)
if reports:
    print(f"    Status: {reports.get('status')}")

# Summary
print("\n" + "=" * 60)
print("TEST RESULTS SUMMARY")
print("=" * 60)
print(f"  Passed: {passed}")
print(f"  Failed: {failed}")
print(f"  Total:  {passed + failed}")
if errors:
    print(f"\n  Errors ({len(errors)}):")
    for e in errors:
        print(f"    {e}")
print("=" * 60)

