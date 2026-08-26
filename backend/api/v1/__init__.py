from fastapi import APIRouter

from backend.api.v1 import auth, budgets, expenses, finance, incomes, system, users, ai

router = APIRouter()
router.include_router(system.router)
router.include_router(auth.router)
router.include_router(users.router)
router.include_router(incomes.router)
router.include_router(expenses.router)
router.include_router(budgets.router)
router.include_router(finance.router)
router.include_router(ai.router)

