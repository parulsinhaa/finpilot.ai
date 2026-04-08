"""
FinPilot AI — Medium Task: Debt Payoff
Goal: Pay off all high-interest debt within 24 months.
"""

TASK_META = {
    "name": "debt_payoff",
    "difficulty": "medium",
    "max_steps": 24,
    "description": "Eliminate high-interest debt while maintaining savings.",
    "success_criteria": {
        "high_interest_debt_remaining": 0,
        "savings_rate_min": 0.15,
        "months_limit": 24,
    },
    "tips": [
        "Use the debt avalanche method: highest interest first",
        "Every extra rupee on debt saves compounded interest",
        "Don't stop investing entirely — maintain SIP",
        "Build 3-month emergency fund before aggressive payoff",
    ],
    "initial_state": {
        "income": 75000,
        "savings": 40000,
        "debt": 350000,
        "investments": 15000,
        "emergency_fund": 30000,
        "expense_ratio": 0.65,
        "debt_interest_rate": 14.5,
        "monthly_debt_payment": 12000,
    }
}