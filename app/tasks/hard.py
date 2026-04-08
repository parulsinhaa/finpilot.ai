"""
FinPilot AI — Hard Task: Wealth Building
Goal: Triple net worth in 36 months with health score >= 70.
"""

TASK_META = {
    "name": "wealth_building",
    "difficulty": "hard",
    "max_steps": 36,
    "description": "Build serious wealth — 3x net worth growth in 3 years.",
    "success_criteria": {
        "net_worth_multiplier": 3.0,
        "health_score_min": 70,
        "months_limit": 36,
    },
    "tips": [
        "Maximise investment allocation — compound returns are powerful",
        "Pay off debt aggressively in first 12 months",
        "Diversify: index funds, debt funds, and real estate SIPs",
        "Maintain 6-month emergency fund as a base",
        "Review and rebalance portfolio every quarter",
        "Manage life events: medical insurance is critical",
    ],
    "initial_state": {
        "income": 100000,
        "savings": 80000,
        "debt": 200000,
        "investments": 50000,
        "emergency_fund": 60000,
        "expense_ratio": 0.58,
        "debt_interest_rate": 10.5,
        "monthly_debt_payment": 10000,
        "sip_amount": 8000,
    }
}