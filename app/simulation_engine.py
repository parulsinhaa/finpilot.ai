"""
FinPilot AI — Financial Simulation Engine
Simulates a person's complete financial life month-by-month.
Includes income, expenses, savings, debt, investments, inflation,
and stochastic life events.
"""

import random
import numpy as np
from typing import Optional
from app.calculators import (
    financial_health_score, inflation_adjusted_value,
    emergency_fund_required, emi
)


# ─────────────────────────────────────────────
#  Life Events Engine
# ─────────────────────────────────────────────

LIFE_EVENTS = {
    "none":               {"probability": 0.72, "label": "Normal month"},
    "salary_increase":    {"probability": 0.07, "label": "Salary Increase",  "impact": "positive"},
    "medical_emergency":  {"probability": 0.06, "label": "Medical Emergency","impact": "negative"},
    "job_loss":           {"probability": 0.03, "label": "Job Loss",          "impact": "negative"},
    "market_crash":       {"probability": 0.04, "label": "Market Crash",      "impact": "negative"},
    "windfall":           {"probability": 0.03, "label": "Unexpected Windfall","impact": "positive"},
    "promotion":          {"probability": 0.03, "label": "Promotion",         "impact": "positive"},
    "expense_spike":      {"probability": 0.02, "label": "Expense Spike",     "impact": "negative"},
}

DEFAULT_EXPENSE_CATEGORIES = {
    "housing":      0.30,   # Rent / EMI
    "food":         0.15,
    "transport":    0.08,
    "utilities":    0.05,
    "healthcare":   0.04,
    "education":    0.05,
    "entertainment":0.06,
    "clothing":     0.04,
    "personal_care":0.03,
    "miscellaneous":0.05,
}


class SimulationEngine:
    """
    Core financial simulation engine.
    One call to simulate_month() advances time by one month.
    """

    def __init__(self, initial_state: dict, seed: Optional[int] = None):
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

        self.state = self._init_state(initial_state)
        self.history = []

    def _init_state(self, params: dict) -> dict:
        income = params.get("income", 80000)
        monthly_expenses = income * params.get("expense_ratio", 0.65)
        debt = params.get("debt", 150000)

        # Build expense categories
        expense_ratio = params.get("expense_categories", DEFAULT_EXPENSE_CATEGORIES)
        expenses = {cat: round(income * ratio, 2)
                    for cat, ratio in expense_ratio.items()}

        state = {
            # Identity
            "month": 0,
            "currency": params.get("currency", "INR"),

            # Income & Expenses
            "income": income,
            "expenses": expenses,
            "monthly_expenses": monthly_expenses,
            "monthly_surplus": income - monthly_expenses,

            # Balance sheet
            "savings": params.get("savings", 50000),
            "debt": debt,
            "investments": params.get("investments", 20000),
            "emergency_fund": params.get("emergency_fund", 30000),
            "net_worth": params.get("savings", 50000) + params.get("investments", 20000) - debt,
            "initial_net_worth": 0,  # set after first calc

            # Investment details
            "sip_amount": params.get("sip_amount", 5000),
            "investment_return_rate": params.get("investment_return_rate", 12.0),
            "debt_interest_rate": params.get("debt_interest_rate", 12.0),
            "monthly_debt_payment": params.get("monthly_debt_payment", 8000),

            # Macro
            "inflation_rate": params.get("inflation_rate", 6.0),
            "market_sentiment": "neutral",  # bullish / neutral / bearish

            # Life events
            "life_event": "none",
            "life_event_impact": 0.0,

            # Metrics
            "health_score": 50,
            "savings_rate": 0.0,
            "net_worth_change_pct": 0.0,
            "streak_days": 0,

            # Goals
            "goals": params.get("goals", []),

            # Flags
            "employed": True,
            "job_loss_months_remaining": 0,
        }

        # Recalculate derived values
        state = self._recalculate(state)
        state["initial_net_worth"] = state["net_worth"]
        return state

    # ──────────────────────────────────────────
    #  Public API
    # ──────────────────────────────────────────

    def simulate_month(self, action: dict) -> dict:
        """Advance simulation by one month. Returns new state."""
        prev_state = {k: v for k, v in self.state.items()
                      if not isinstance(v, (dict, list))}

        self.state["month"] += 1

        # 1. Apply macro changes
        self._apply_inflation()
        self._apply_market_returns()

        # 2. Roll life event
        event = self._roll_life_event()
        self.state["life_event"] = event
        self._apply_life_event(event)

        # 3. Process income
        if self.state["employed"]:
            net_income = self.state["income"]
        else:
            net_income = self.state["income"] * 0.0  # unemployed
            self.state["job_loss_months_remaining"] = max(
                0, self.state["job_loss_months_remaining"] - 1
            )
            if self.state["job_loss_months_remaining"] == 0:
                self.state["employed"] = True

        # 4. Process debt (minimum payment)
        if self.state["debt"] > 0:
            interest = self.state["debt"] * self.state["debt_interest_rate"] / (12 * 100)
            min_payment = min(self.state["monthly_debt_payment"],
                              self.state["debt"] + interest)
            self.state["debt"] = max(0, self.state["debt"] + interest - min_payment)
            net_income -= min_payment

        # 5. Process expenses
        net_income -= self.state["monthly_expenses"]

        # 6. Process SIP investments (auto)
        if self.state["sip_amount"] > 0 and net_income >= self.state["sip_amount"]:
            self.state["investments"] += self.state["sip_amount"]
            net_income -= self.state["sip_amount"]

        # 7. Apply agent action
        net_income = self._apply_action(action, net_income)

        # 8. Add any remaining surplus to savings
        if net_income > 0:
            self.state["savings"] += net_income * 0.5  # half to savings
        elif net_income < 0:
            # Draw from emergency fund or savings
            shortfall = abs(net_income)
            if self.state["emergency_fund"] >= shortfall:
                self.state["emergency_fund"] -= shortfall
            elif self.state["savings"] >= shortfall:
                self.state["savings"] -= shortfall
            else:
                # Take micro-debt
                self.state["debt"] += shortfall

        # 9. Update streak
        if net_income >= 0 and self.state["life_event"] not in ["job_loss", "medical_emergency"]:
            self.state["streak_days"] = min(365, self.state["streak_days"] + 30)
        else:
            self.state["streak_days"] = max(0, self.state["streak_days"] - 15)

        # 10. Recalculate all metrics
        self.state = self._recalculate(self.state)
        self.history.append({k: v for k, v in self.state.items()
                              if not isinstance(v, list)})

        return {"state": self.state, "prev_state": prev_state,
                "done": self._is_done()}

    def get_state(self) -> dict:
        return self.state

    def get_history(self) -> list:
        return self.history

    # ──────────────────────────────────────────
    #  Internal helpers
    # ──────────────────────────────────────────

    def _recalculate(self, state: dict) -> dict:
        """Recalculate all derived metrics from raw state."""
        income = max(state["income"], 1)

        # Net worth
        state["net_worth"] = (state["savings"] + state["investments"]
                               + state["emergency_fund"] - state["debt"])

        # Savings rate
        monthly_savings = max(0, state["income"] - state["monthly_expenses"]
                               - state.get("monthly_debt_payment", 0))
        state["savings_rate"] = round(monthly_savings / income, 4)

        # Monthly surplus
        state["monthly_surplus"] = round(
            state["income"] - state["monthly_expenses"]
            - state.get("monthly_debt_payment", 0), 2
        )

        # Total monthly expenses
        state["monthly_expenses"] = round(
            sum(v for v in state["expenses"].values()
                if isinstance(v, (int, float))), 2
        )

        # Net worth change %
        initial = state.get("initial_net_worth", state["net_worth"])
        if initial != 0:
            state["net_worth_change_pct"] = round(
                (state["net_worth"] - initial) / abs(initial), 4
            )

        # Health score
        state["health_score"] = financial_health_score(state)

        # Emergency fund adequacy
        ef_req = emergency_fund_required(
            state["monthly_expenses"],
            months_coverage=6,
            has_dependents=False
        )
        state["emergency_fund_months"] = round(
            state["emergency_fund"] / max(state["monthly_expenses"], 1), 2
        )
        state["emergency_fund_required"] = ef_req["recommended_amount"]

        return state

    def _apply_inflation(self):
        """Apply monthly inflation to expenses."""
        monthly_inflation = self.state["inflation_rate"] / (12 * 100)
        for cat in self.state["expenses"]:
            self.state["expenses"][cat] = round(
                self.state["expenses"][cat] * (1 + monthly_inflation), 2
            )

    def _apply_market_returns(self):
        """Apply monthly investment return with market volatility."""
        base_return = self.state["investment_return_rate"] / (12 * 100)

        # Stochastic return: normal distribution around base
        volatility = 0.015  # 1.5% monthly std dev
        actual_return = np.random.normal(base_return, volatility)

        # Sentiment modifiers
        sentiment_multiplier = {"bullish": 1.3, "neutral": 1.0, "bearish": 0.7}
        actual_return *= sentiment_multiplier.get(self.state["market_sentiment"], 1.0)

        self.state["investments"] = max(
            0, self.state["investments"] * (1 + actual_return)
        )

    def _roll_life_event(self) -> str:
        """Randomly select a life event based on probability weights."""
        events = list(LIFE_EVENTS.keys())
        probs = [LIFE_EVENTS[e]["probability"] for e in events]
        return random.choices(events, weights=probs, k=1)[0]

    def _apply_life_event(self, event: str):
        """Apply financial impact of life event to state."""
        income = self.state["income"]

        if event == "salary_increase":
            increase = random.uniform(0.05, 0.25)
            self.state["income"] = round(self.state["income"] * (1 + increase), 2)
            self.state["life_event_impact"] = round(increase * income, 2)

        elif event == "promotion":
            increase = random.uniform(0.15, 0.40)
            self.state["income"] = round(self.state["income"] * (1 + increase), 2)
            self.state["life_event_impact"] = round(increase * income, 2)

        elif event == "medical_emergency":
            cost = random.uniform(20000, 200000)
            if self.state["emergency_fund"] >= cost:
                self.state["emergency_fund"] -= cost
            else:
                remainder = cost - self.state["emergency_fund"]
                self.state["emergency_fund"] = 0
                self.state["debt"] += remainder
            self.state["life_event_impact"] = -round(cost, 2)

        elif event == "job_loss":
            self.state["employed"] = False
            self.state["job_loss_months_remaining"] = random.randint(2, 6)
            self.state["life_event_impact"] = -round(income, 2)
            self.state["market_sentiment"] = "bearish"

        elif event == "market_crash":
            crash_pct = random.uniform(0.15, 0.40)
            loss = self.state["investments"] * crash_pct
            self.state["investments"] *= (1 - crash_pct)
            self.state["market_sentiment"] = "bearish"
            self.state["life_event_impact"] = -round(loss, 2)

        elif event == "windfall":
            amount = random.uniform(50000, 500000)
            self.state["savings"] += amount
            self.state["life_event_impact"] = round(amount, 2)

        elif event == "expense_spike":
            extra = random.uniform(10000, 50000)
            self.state["expenses"]["miscellaneous"] = (
                self.state["expenses"].get("miscellaneous", 0) + extra
            )
            self.state["life_event_impact"] = -round(extra, 2)

        else:
            self.state["life_event_impact"] = 0.0
            # Recover market sentiment gradually
            if self.state["market_sentiment"] == "bearish":
                if random.random() > 0.7:
                    self.state["market_sentiment"] = "neutral"
            elif self.state["market_sentiment"] == "neutral":
                if random.random() > 0.8:
                    self.state["market_sentiment"] = "bullish"

    def _apply_action(self, action: dict, surplus: float) -> float:
        """Apply agent action and return updated surplus."""
        action_type = action.get("type", "save")
        params = action.get("params", {})
        amount = params.get("amount", 0)

        if action_type == "save":
            transfer = min(amount, surplus)
            self.state["savings"] += transfer
            surplus -= transfer

        elif action_type == "invest_sip":
            transfer = min(amount, surplus)
            self.state["investments"] += transfer
            self.state["sip_amount"] = amount  # Update ongoing SIP
            surplus -= transfer

        elif action_type == "repay_debt":
            if self.state["debt"] > 0:
                payment = min(amount, surplus, self.state["debt"])
                self.state["debt"] = max(0, self.state["debt"] - payment)
                surplus -= payment

        elif action_type == "build_emergency_fund":
            transfer = min(amount, surplus)
            self.state["emergency_fund"] += transfer
            surplus -= transfer

        elif action_type == "adjust_expenses":
            category = params.get("category", "miscellaneous")
            new_amount = params.get("new_amount", 0)
            if category in self.state["expenses"]:
                old = self.state["expenses"][category]
                self.state["expenses"][category] = max(0, new_amount)
                surplus += (old - new_amount)  # freed up or used more

        elif action_type == "withdraw_investment":
            if self.state["investments"] >= amount:
                penalty = amount * 0.05 if self.state["month"] < 12 else 0
                self.state["investments"] -= amount
                self.state["savings"] += amount - penalty
                surplus += amount - penalty

        elif action_type == "take_loan":
            interest_rate = params.get("interest_rate", 12.0)
            self.state["debt"] += amount
            self.state["debt_interest_rate"] = (
                (self.state["debt_interest_rate"] + interest_rate) / 2
            )
            self.state["savings"] += amount
            surplus += amount

        return surplus

    def _is_done(self) -> bool:
        """Check terminal conditions."""
        # Bankruptcy: negative net worth and no income for 3 months
        if (self.state["net_worth"] < -500000 and
                not self.state["employed"] and
                self.state["savings"] <= 0):
            return True
        return False

    def what_if(self, scenario: dict) -> list:
        """
        Run a what-if scenario: apply scenario changes and simulate N months.
        Returns projected states without modifying actual state.
        """
        import copy
        temp_state = copy.deepcopy(self.state)
        temp_engine = SimulationEngine({"income": temp_state["income"]})
        temp_engine.state = temp_state

        # Apply scenario
        for key, val in scenario.get("state_overrides", {}).items():
            if key in temp_engine.state:
                temp_engine.state[key] = val

        projections = []
        months = scenario.get("months", 12)
        action = scenario.get("action", {"type": "save", "params": {"amount": 10000}})

        for _ in range(months):
            result = temp_engine.simulate_month(action)
            projections.append({
                "month": result["state"]["month"],
                "net_worth": round(result["state"]["net_worth"], 2),
                "savings": round(result["state"]["savings"], 2),
                "investments": round(result["state"]["investments"], 2),
                "health_score": result["state"]["health_score"],
                "debt": round(result["state"]["debt"], 2),
            })

        return projections