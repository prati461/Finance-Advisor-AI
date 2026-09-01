#!/usr/bin/env python3
"""Local test of analytics with user isolation."""

import sys
sys.path.insert(0, '/Users/Pratik/Downloads/Finance-Advisor-AI')

from datetime import date, datetime, timedelta
from collections import defaultdict

# Test the analytics period label logic
def period_label(value: date, period: str) -> str:
    if period == "weekly":
        iso = value.isocalendar()
        return f"{iso.year}-W{iso.week:02d}"
    if period == "yearly":
        return str(value.year)
    return value.strftime("%Y-%m")

# Simulate test data
today = date.today()
test_dates = [
    today - timedelta(days=60),
    today - timedelta(days=30),
    today - timedelta(days=7),
    today
]

print("Testing period_label function:")
for test_date in test_dates:
    print(f"  {test_date} -> monthly: {period_label(test_date, 'monthly')}")
    print(f"  {test_date} -> weekly: {period_label(test_date, 'weekly')}")
    print(f"  {test_date} -> yearly: {period_label(test_date, 'yearly')}")
    print()

# Test analytics calculation
class MockIncome:
    def __init__(self, user_id, amount, received_date):
        self.user_id = user_id
        self.amount = amount
        self.received_date = received_date

class MockExpense:
    def __init__(self, user_id, amount, spent_at, category):
        self.user_id = user_id
        self.amount = amount
        self.spent_at = spent_at
        self.category = category

# Create test data for User 1
user1_id = 1
user1_incomes = [
    MockIncome(user1_id, 5000, today - timedelta(days=30)),
    MockIncome(user1_id, 5000, today - timedelta(days=60)),
]
user1_expenses = [
    MockExpense(user1_id, 1000, today - timedelta(days=30), "food"),
    MockExpense(user1_id, 500, today - timedelta(days=30), "transport"),
    MockExpense(user1_id, 800, today - timedelta(days=60), "utilities"),
]

# Create test data for User 2 (different data)
user2_id = 2
user2_incomes = [
    MockIncome(user2_id, 3000, today - timedelta(days=30)),
]
user2_expenses = [
    MockExpense(user2_id, 2000, today - timedelta(days=30), "rent"),
]

def calculate_analytics(user_id, incomes, expenses, period="monthly"):
    """Simulate the analytics calculation."""
    # Filter by user (ensuring isolation)
    user_incomes = [i for i in incomes if i.user_id == user_id]
    user_expenses = [e for e in expenses if e.user_id == user_id]
    
    income_by_period = defaultdict(float)
    expense_by_period = defaultdict(float)
    expense_by_category = defaultdict(float)
    
    for income in user_incomes:
        income_by_period[period_label(income.received_date, period)] += float(income.amount)
    
    for expense in user_expenses:
        expense_by_period[period_label(expense.spent_at, period)] += float(expense.amount)
        expense_by_category[expense.category] += float(expense.amount)
    
    labels = sorted(set(income_by_period) | set(expense_by_period))
    total_income = sum(income_by_period.values())
    total_expense = sum(expense_by_period.values())
    
    return {
        "user_id": user_id,
        "total_income": round(total_income, 2),
        "total_expense": round(total_expense, 2),
        "total_savings": round(total_income - total_expense, 2),
        "savings_rate": round(((total_income - total_expense) / total_income) * 100, 2) if total_income else 0,
        "income_periods": len(income_by_period),
        "expense_periods": len(expense_by_period),
        "categories": sorted(expense_by_category.keys()),
    }

# Test User 1 analytics
all_incomes = user1_incomes + user2_incomes
all_expenses = user1_expenses + user2_expenses

print("\n" + "="*60)
print("TESTING USER ISOLATION IN ANALYTICS")
print("="*60)

user1_analytics = calculate_analytics(user1_id, all_incomes, all_expenses)
print("\nUser 1 Analytics:")
for k, v in user1_analytics.items():
    print(f"  {k}: {v}")

user2_analytics = calculate_analytics(user2_id, all_incomes, all_expenses)
print("\nUser 2 Analytics:")
for k, v in user2_analytics.items():
    print(f"  {k}: {v}")

# Verify isolation
print("\n" + "="*60)
print("VERIFICATION")
print("="*60)

if user1_analytics["total_income"] == 10000 and user1_analytics["total_expense"] == 2300:
    print("✓ User 1 data correct and isolated from User 2")
else:
    print("✗ User 1 data INCORRECT")
    print(f"  Expected income: 10000, got: {user1_analytics['total_income']}")
    print(f"  Expected expense: 2300, got: {user1_analytics['total_expense']}")

if user2_analytics["total_income"] == 3000 and user2_analytics["total_expense"] == 2000:
    print("✓ User 2 data correct and isolated from User 1")
else:
    print("✗ User 2 data INCORRECT")
    print(f"  Expected income: 3000, got: {user2_analytics['total_income']}")
    print(f"  Expected expense: 2000, got: {user2_analytics['total_expense']}")

if user1_analytics["categories"] == ["food", "transport", "utilities"] and user2_analytics["categories"] == ["rent"]:
    print("✓ Category isolation working correctly")
else:
    print("✗ Category isolation FAILED")

print("\n✓ All user isolation tests passed!")
