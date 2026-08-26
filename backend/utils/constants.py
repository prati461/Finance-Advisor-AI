from enum import Enum


class IncomeCategory(str, Enum):
    SALARY = "Salary"
    BUSINESS = "Business"
    FREELANCE = "Freelance"
    INVESTMENT = "Investment"
    OTHER = "Other"


class ExpenseCategory(str, Enum):
    FOOD = "Food"
    UTILITIES = "Utilities"
    RENT = "Rent"
    TRANSPORTATION = "Transportation"
    ENTERTAINMENT = "Entertainment"
    HEALTH = "Health"
    SHOPPING = "Shopping"
    EDUCATION = "Education"
    OTHER = "Other"


class IncomeFrequency(str, Enum):
    ONE_TIME = "One-time"
    WEEKLY = "Weekly"
    BIWEEKLY = "Biweekly"
    MONTHLY = "Monthly"
    ANNUAL = "Annual"
