"""
FinPilot AI — Easy Task: Budget Balance
Goal: Achieve 20%+ savings rate for 6 consecutive months.
"""

TASK_META = {
    "name": "budget_balance",
    "difficulty": "easy",
    "max_steps": 12,
    "description": "Balance your budget and achieve a sustainable savings rate.",
    "success_criteria": {
        "savings_rate_min": 0.20,
        "consecutive_months": 6,
    },
    "tips": [
        "Track every expense category",
        "Identify and reduce discretionary spending",
        "Automate savings transfers on payday",
        "Use the 50/30/20 rule: needs/wants/savings",
    ],
    "initial_state": {
        "income": 60000,
        "savings": 20000,
        "debt": 80000,
        "investments": 5000,
        "emergency_fund": 10000,
        "expense_ratio": 0.75,
        "debt_interest_rate": 16.0,
        "monthly_debt_payment": 6000,
    }
}