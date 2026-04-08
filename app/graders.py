"""
FinPilot AI — Graders & Reward Functions
All rewards normalised strictly between 0.0 and 1.0.
"""


def get_grader(task: str):
    graders = {
        "budget_balance": BudgetBalanceGrader(),
        "debt_payoff": DebtPayoffGrader(),
        "wealth_building": WealthBuildingGrader(),
    }
    return graders.get(task, WealthBuildingGrader())


class BudgetBalanceGrader:
    """Easy task: Achieve 20%+ savings rate for 6 consecutive months."""

    def step_reward(self, state: dict, prev_state: dict, action: dict) -> float:
        reward = 0.0
        sr = state.get("savings_rate", 0)

        # Savings rate reward (50%)
        if sr >= 0.20:   reward += 0.50
        elif sr >= 0.10: reward += 0.25
        elif sr >= 0.05: reward += 0.10

        # Positive surplus (25%)
        surplus = state.get("monthly_surplus", 0)
        if surplus > 0:
            reward += min(surplus / state.get("income", 1), 0.25)

        # Health score (25%)
        reward += (state.get("health_score", 0) / 100) * 0.25

        return round(min(1.0, max(0.0, reward)), 6)

    def episode_reward(self, final_state: dict, history: list) -> float:
        if not history: return 0.0

        # Consecutive months with 20%+ savings rate
        streak = 0
        max_streak = 0
        for h in history:
            if h.get("savings_rate", 0) >= 0.20:
                streak += 1
                max_streak = max(max_streak, streak)
            else:
                streak = 0

        base = min(max_streak / 6, 1.0) * 0.6
        avg_health = sum(h.get("health_score", 0) for h in history) / len(history)
        health_bonus = (avg_health / 100) * 0.4
        return round(min(1.0, base + health_bonus), 6)

    def is_success(self, state: dict) -> bool:
        return state.get("savings_rate", 0) >= 0.20 and state.get("health_score", 0) >= 60

    def summary(self, state: dict, history: list) -> str:
        sr = state.get("savings_rate", 0)
        return (f"Savings rate: {sr*100:.1f}% "
                f"({'achieved' if sr >= 0.20 else 'below'} 20% target). "
                f"Health score: {state.get('health_score', 0)}/100.")


class DebtPayoffGrader:
    """Medium task: Pay off high-interest debt within 24 months."""

    def step_reward(self, state: dict, prev_state: dict, action: dict) -> float:
        reward = 0.0

        # Debt reduction (50%)
        debt_prev = prev_state.get("debt", 0)
        debt_curr = state.get("debt", 0)
        if debt_prev > 0:
            reduction_pct = (debt_prev - debt_curr) / debt_prev
            reward += min(reduction_pct * 5, 0.50)

        # Maintained savings (30%)
        sr = state.get("savings_rate", 0)
        if sr >= 0.15: reward += 0.30
        elif sr >= 0.10: reward += 0.15

        # Health improvement (20%)
        health_prev = prev_state.get("health_score", 0)
        health_curr = state.get("health_score", 0)
        improvement = (health_curr - health_prev) / 100
        reward += max(0, improvement) * 0.20 + (health_curr / 100) * 0.10

        return round(min(1.0, max(0.0, reward)), 6)

    def episode_reward(self, final_state: dict, history: list) -> float:
        initial_debt = history[0].get("debt", 1) if history else 1
        final_debt = final_state.get("debt", initial_debt)
        debt_paid_pct = max(0, (initial_debt - final_debt) / max(initial_debt, 1))

        speed_bonus = 0.0
        if debt_paid_pct >= 1.0:
            months_taken = final_state.get("month", 24)
            speed_bonus = max(0, (24 - months_taken) / 24) * 0.20

        avg_sr = sum(h.get("savings_rate", 0) for h in history) / max(len(history), 1)
        sr_bonus = min(avg_sr / 0.15, 1.0) * 0.20

        base = min(debt_paid_pct, 1.0) * 0.60
        return round(min(1.0, base + speed_bonus + sr_bonus), 6)

    def is_success(self, state: dict) -> bool:
        return state.get("debt", 0) == 0 or (
            state.get("debt", 0) < 50000 and state.get("health_score", 0) >= 70
        )

    def summary(self, state: dict, history: list) -> str:
        debt = state.get("debt", 0)
        return (f"Remaining debt: {debt:,.0f}. "
                f"{'Debt cleared!' if debt == 0 else 'Keep paying down.'} "
                f"Health score: {state.get('health_score', 0)}/100.")


class WealthBuildingGrader:
    """Hard task: Triple net worth in 36 months with health score ≥ 70."""

    def step_reward(self, state: dict, prev_state: dict, action: dict) -> float:
        reward = 0.0

        # Net worth progress toward 3x target (40%)
        initial_nw = state.get("initial_net_worth", state.get("net_worth", 1))
        curr_nw = state.get("net_worth", 0)
        target_nw = initial_nw * 3
        progress = max(0, (curr_nw - initial_nw) / max(target_nw - initial_nw, 1))
        reward += min(progress, 1.0) * 0.40

        # Investment growth (30%)
        inv_prev = prev_state.get("investments", 0)
        inv_curr = state.get("investments", 0)
        if inv_prev > 0:
            inv_growth = (inv_curr - inv_prev) / inv_prev
            reward += max(0, min(inv_growth * 3, 0.30))

        # Health score ≥ 70 maintained (20%)
        health = state.get("health_score", 0)
        if health >= 70: reward += 0.20
        elif health >= 55: reward += 0.10

        # Debt reduction (10%)
        debt_prev = prev_state.get("debt", 0)
        debt_curr = state.get("debt", 0)
        if debt_prev > 0:
            reduction = (debt_prev - debt_curr) / debt_prev
            reward += max(0, reduction) * 0.10

        return round(min(1.0, max(0.0, reward)), 6)

    def episode_reward(self, final_state: dict, history: list) -> float:
        if not history: return 0.0

        initial_nw = history[0].get("net_worth", 1) if history else 1
        final_nw = final_state.get("net_worth", 0)
        target_nw = initial_nw * 3

        nw_score = min(max(0, (final_nw - initial_nw) / max(target_nw - initial_nw, 1)), 1.0)

        avg_health = sum(h.get("health_score", 0) for h in history) / max(len(history), 1)
        health_score = min(avg_health / 70, 1.0)

        # Consistency bonus
        positive_months = sum(1 for h in history if h.get("monthly_surplus", 0) > 0)
        consistency = positive_months / max(len(history), 1)

        return round(
            min(1.0, nw_score * 0.50 + health_score * 0.30 + consistency * 0.20),
            6
        )

    def is_success(self, state: dict) -> bool:
        initial = state.get("initial_net_worth", 1)
        return (state.get("net_worth", 0) >= initial * 3 and
                state.get("health_score", 0) >= 70)

    def summary(self, state: dict, history: list) -> str:
        initial = history[0].get("net_worth", 1) if history else 1
        current = state.get("net_worth", 0)
        target = initial * 3
        progress = (current - initial) / max(target - initial, 1) * 100
        return (f"Net worth progress: {progress:.1f}% toward 3x goal "
                f"({current:,.0f} / {target:,.0f}). "
                f"Health score: {state.get('health_score', 0)}/100.")