"""
FinPilot AI — Financial Calculators
All calculators are pure functions used both in the UI and simulation engine.
"""

import math
from typing import Optional


# ─────────────────────────────────────────────
#  EMI Calculator
# ─────────────────────────────────────────────

def emi(principal: float, annual_rate: float, months: int) -> dict:
    """
    Calculate EMI, total payment, and total interest.
    annual_rate: percentage (e.g. 8.5 for 8.5%)
    """
    if annual_rate == 0:
        monthly_emi = principal / months
        return {
            "emi": round(monthly_emi, 2),
            "total_payment": round(monthly_emi * months, 2),
            "total_interest": 0.0,
            "principal": round(principal, 2),
        }

    r = annual_rate / (12 * 100)
    e = principal * r * (1 + r) ** months / ((1 + r) ** months - 1)
    total = e * months

    return {
        "emi": round(e, 2),
        "total_payment": round(total, 2),
        "total_interest": round(total - principal, 2),
        "principal": round(principal, 2),
        "monthly_rate": round(r * 100, 4),
    }


def emi_amortisation(principal: float, annual_rate: float, months: int) -> list:
    """Return month-by-month amortisation schedule."""
    r = annual_rate / (12 * 100) if annual_rate else 0
    monthly_emi = emi(principal, annual_rate, months)["emi"]
    balance = principal
    schedule = []

    for m in range(1, months + 1):
        interest_paid = balance * r
        principal_paid = monthly_emi - interest_paid
        balance = max(0, balance - principal_paid)
        schedule.append({
            "month": m,
            "emi": round(monthly_emi, 2),
            "principal_paid": round(principal_paid, 2),
            "interest_paid": round(interest_paid, 2),
            "balance": round(balance, 2),
        })

    return schedule


# ─────────────────────────────────────────────
#  SIP (Systematic Investment Plan) Calculator
# ─────────────────────────────────────────────

def sip_future_value(monthly_amount: float, annual_return: float, years: int) -> dict:
    """
    Calculate SIP future value using compound interest.
    annual_return: percentage (e.g. 12 for 12%)
    """
    r = annual_return / (12 * 100)
    n = years * 12
    total_invested = monthly_amount * n

    if r == 0:
        fv = total_invested
    else:
        fv = monthly_amount * ((1 + r) ** n - 1) / r * (1 + r)

    return {
        "future_value": round(fv, 2),
        "total_invested": round(total_invested, 2),
        "total_returns": round(fv - total_invested, 2),
        "wealth_ratio": round(fv / total_invested, 4) if total_invested > 0 else 1.0,
        "cagr": round(annual_return, 2),
    }


def sip_required_monthly(target: float, annual_return: float, years: int) -> float:
    """Calculate monthly SIP needed to reach a target corpus."""
    r = annual_return / (12 * 100)
    n = years * 12
    if r == 0:
        return target / n
    monthly = target / (((1 + r) ** n - 1) / r * (1 + r))
    return round(monthly, 2)


def sip_growth_series(monthly_amount: float, annual_return: float, years: int) -> list:
    """Return year-by-year SIP growth for charting."""
    series = []
    for y in range(1, years + 1):
        result = sip_future_value(monthly_amount, annual_return, y)
        series.append({
            "year": y,
            "invested": result["total_invested"],
            "value": result["future_value"],
            "returns": result["total_returns"],
        })
    return series


# ─────────────────────────────────────────────
#  Compound Growth
# ─────────────────────────────────────────────

def compound_growth(principal: float, annual_rate: float, years: int,
                    compounding: str = "monthly") -> dict:
    """
    Calculate compound growth.
    compounding: 'daily' | 'monthly' | 'quarterly' | 'annually'
    """
    n_map = {"daily": 365, "monthly": 12, "quarterly": 4, "annually": 1}
    n = n_map.get(compounding, 12)
    r = annual_rate / 100
    fv = principal * (1 + r / n) ** (n * years)

    return {
        "future_value": round(fv, 2),
        "total_interest": round(fv - principal, 2),
        "principal": round(principal, 2),
        "effective_rate": round(((1 + r / n) ** n - 1) * 100, 4),
        "compounding": compounding,
    }


def inflation_adjusted_value(amount: float, inflation_rate: float, years: int) -> dict:
    """Calculate purchasing power after inflation erosion."""
    r = inflation_rate / 100
    real_value = amount / (1 + r) ** years
    return {
        "nominal_amount": round(amount, 2),
        "real_value": round(real_value, 2),
        "purchasing_power_loss": round(amount - real_value, 2),
        "loss_percentage": round((1 - real_value / amount) * 100, 2),
    }


# ─────────────────────────────────────────────
#  Net Worth Calculator
# ─────────────────────────────────────────────

def net_worth(assets: dict, liabilities: dict) -> dict:
    """
    assets: {savings, investments, property, other}
    liabilities: {home_loan, car_loan, personal_loan, credit_card, other}
    """
    total_assets = sum(v for v in assets.values() if isinstance(v, (int, float)))
    total_liabilities = sum(v for v in liabilities.values() if isinstance(v, (int, float)))
    nw = total_assets - total_liabilities
    debt_to_asset = total_liabilities / total_assets if total_assets > 0 else 0

    return {
        "net_worth": round(nw, 2),
        "total_assets": round(total_assets, 2),
        "total_liabilities": round(total_liabilities, 2),
        "debt_to_asset_ratio": round(debt_to_asset, 4),
        "asset_breakdown": {k: round(v, 2) for k, v in assets.items()},
        "liability_breakdown": {k: round(v, 2) for k, v in liabilities.items()},
    }


# ─────────────────────────────────────────────
#  Emergency Fund Calculator
# ─────────────────────────────────────────────

def emergency_fund_required(monthly_expenses: float,
                             months_coverage: int = 6,
                             has_dependents: bool = False,
                             job_stability: str = "stable") -> dict:
    """
    Calculate required emergency fund.
    job_stability: 'very_stable' | 'stable' | 'moderate' | 'unstable'
    """
    stability_multiplier = {
        "very_stable": 3, "stable": 6, "moderate": 9, "unstable": 12
    }
    recommended_months = stability_multiplier.get(job_stability, 6)
    if has_dependents:
        recommended_months = min(recommended_months + 3, 18)

    required = monthly_expenses * recommended_months
    minimum = monthly_expenses * 3

    return {
        "recommended_amount": round(required, 2),
        "minimum_amount": round(minimum, 2),
        "recommended_months": recommended_months,
        "monthly_expenses": round(monthly_expenses, 2),
        "rationale": f"{recommended_months} months for {job_stability} job stability"
                     + (" with dependents" if has_dependents else ""),
    }


# ─────────────────────────────────────────────
#  Debt Payoff Calculator (Avalanche + Snowball)
# ─────────────────────────────────────────────

def debt_payoff_avalanche(debts: list, monthly_extra: float = 0) -> dict:
    """
    Debt avalanche method: pay highest interest first.
    debts: [{"name": str, "balance": float, "rate": float, "min_payment": float}]
    """
    import copy
    debts_copy = copy.deepcopy(debts)
    month = 0
    total_interest = 0
    schedule = []

    while any(d["balance"] > 0 for d in debts_copy):
        month += 1
        if month > 600:  # 50-year safety cap
            break

        # Sort by interest rate descending
        active = sorted([d for d in debts_copy if d["balance"] > 0],
                        key=lambda x: x["rate"], reverse=True)

        extra_pool = monthly_extra
        month_interest = 0

        for i, debt in enumerate(debts_copy):
            if debt["balance"] <= 0:
                continue
            interest = debt["balance"] * debt["rate"] / (12 * 100)
            month_interest += interest
            payment = debt["min_payment"]
            if active and active[0]["name"] == debt["name"] and extra_pool > 0:
                payment += extra_pool
                extra_pool = 0
            actual_payment = min(payment, debt["balance"] + interest)
            debt["balance"] = max(0, debt["balance"] + interest - actual_payment)

        total_interest += month_interest
        schedule.append({"month": month, "interest_paid": round(month_interest, 2)})

    return {
        "months_to_payoff": month,
        "total_interest": round(total_interest, 2),
        "method": "avalanche",
        "schedule_length": len(schedule),
    }


def debt_payoff_snowball(debts: list, monthly_extra: float = 0) -> dict:
    """
    Debt snowball method: pay smallest balance first.
    """
    import copy
    debts_copy = copy.deepcopy(debts)
    month = 0
    total_interest = 0

    while any(d["balance"] > 0 for d in debts_copy):
        month += 1
        if month > 600:
            break

        active = sorted([d for d in debts_copy if d["balance"] > 0],
                        key=lambda x: x["balance"])
        extra_pool = monthly_extra

        for debt in debts_copy:
            if debt["balance"] <= 0:
                continue
            interest = debt["balance"] * debt["rate"] / (12 * 100)
            total_interest += interest
            payment = debt["min_payment"]
            if active and active[0]["name"] == debt["name"] and extra_pool > 0:
                payment += extra_pool
                extra_pool = 0
            actual_payment = min(payment, debt["balance"] + interest)
            debt["balance"] = max(0, debt["balance"] + interest - actual_payment)

    return {
        "months_to_payoff": month,
        "total_interest": round(total_interest, 2),
        "method": "snowball",
    }


# ─────────────────────────────────────────────
#  Financial Health Score
# ─────────────────────────────────────────────

def financial_health_score(state: dict) -> int:
    """
    Calculate a 0-100 financial health score.
    Factors: savings rate, debt ratio, emergency fund, net worth growth, investments.
    """
    score = 0
    income = state.get("income", 1)

    # 1. Savings Rate (0-25 points)
    savings_rate = state.get("savings_rate", 0)
    if savings_rate >= 0.30: score += 25
    elif savings_rate >= 0.20: score += 20
    elif savings_rate >= 0.10: score += 12
    elif savings_rate > 0: score += 5

    # 2. Debt-to-Income Ratio (0-25 points)
    monthly_debt = state.get("monthly_debt_payment", 0)
    dti = monthly_debt / income if income > 0 else 1
    if dti <= 0.10: score += 25
    elif dti <= 0.20: score += 20
    elif dti <= 0.35: score += 12
    elif dti <= 0.50: score += 5

    # 3. Emergency Fund (0-20 points)
    monthly_expenses = state.get("monthly_expenses", income * 0.7)
    ef_months = state.get("emergency_fund", 0) / monthly_expenses if monthly_expenses > 0 else 0
    if ef_months >= 6: score += 20
    elif ef_months >= 3: score += 14
    elif ef_months >= 1: score += 7

    # 4. Investment Rate (0-15 points)
    invest_rate = state.get("investments", 0) / (income * 12) if income > 0 else 0
    if invest_rate >= 1.0: score += 15
    elif invest_rate >= 0.5: score += 10
    elif invest_rate >= 0.2: score += 5

    # 5. Net Worth Growth (0-15 points)
    nw_change = state.get("net_worth_change_pct", 0)
    if nw_change >= 0.15: score += 15
    elif nw_change >= 0.08: score += 10
    elif nw_change >= 0: score += 5
    elif nw_change < -0.05: score -= 5

    return max(0, min(100, score))


# ─────────────────────────────────────────────
#  Inflation-Adjusted Projection
# ─────────────────────────────────────────────

def inflation_projection(current_amount: float, annual_growth: float,
                          inflation_rate: float, years: int) -> list:
    """Year-by-year nominal vs real value projection."""
    series = []
    for y in range(1, years + 1):
        nominal = current_amount * (1 + annual_growth / 100) ** y
        real = nominal / (1 + inflation_rate / 100) ** y
        series.append({
            "year": y,
            "nominal": round(nominal, 2),
            "real": round(real, 2),
            "inflation_erosion": round(nominal - real, 2),
        })
    return series


# ─────────────────────────────────────────────
#  Goal Planner
# ─────────────────────────────────────────────

def goal_monthly_saving(target: float, current_savings: float,
                         annual_return: float, years: int) -> dict:
    """How much to save monthly to reach a goal."""
    gap = target - current_savings
    if gap <= 0:
        return {"monthly_saving": 0, "already_reached": True, "gap": 0}

    monthly = sip_required_monthly(gap, annual_return, years)
    return {
        "monthly_saving": monthly,
        "gap": round(gap, 2),
        "target": round(target, 2),
        "years": years,
        "annual_return": annual_return,
        "already_reached": False,
    }