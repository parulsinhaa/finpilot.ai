"""
FinPilot AI — OpenEnv Environment
Implements step(), reset(), state() APIs as per OpenEnv specification.
"""

import os
import yaml
from typing import Optional
from app.simulation_engine import SimulationEngine
from app.ai_engine import AIEngine


TASK_CONFIGS = {
    "budget_balance": {
        "max_steps": 12,
        "initial_state": {
            "income": 60000, "savings": 20000, "debt": 80000,
            "investments": 5000, "emergency_fund": 10000,
            "expense_ratio": 0.75, "debt_interest_rate": 16.0,
            "monthly_debt_payment": 6000,
        },
        "description": "Achieve positive cash flow and 20%+ savings rate for 6 months.",
    },
    "debt_payoff": {
        "max_steps": 24,
        "initial_state": {
            "income": 75000, "savings": 40000, "debt": 350000,
            "investments": 15000, "emergency_fund": 30000,
            "expense_ratio": 0.65, "debt_interest_rate": 14.5,
            "monthly_debt_payment": 12000,
        },
        "description": "Pay off all high-interest debt within 24 months.",
    },
    "wealth_building": {
        "max_steps": 36,
        "initial_state": {
            "income": 100000, "savings": 80000, "debt": 200000,
            "investments": 50000, "emergency_fund": 60000,
            "expense_ratio": 0.58, "debt_interest_rate": 10.5,
            "monthly_debt_payment": 10000,
            "sip_amount": 8000,
        },
        "description": "Triple net worth in 36 months with health score ≥ 70.",
    },
}


class FinPilotEnv:
    """
    OpenEnv-compliant environment for FinPilot AI.
    
    Usage:
        env = FinPilotEnv(task="wealth_building")
        state = env.reset()
        result = env.step({"type": "invest_sip", "params": {"amount": 10000}})
        current = env.state()
    """

    def __init__(self, task: str = "wealth_building", language: str = "English",
                 currency: str = "INR", seed: Optional[int] = None):
        self.task = task
        self.language = language
        self.currency = currency
        self.seed = seed
        self.task_config = TASK_CONFIGS.get(task, TASK_CONFIGS["wealth_building"])

        self.engine: Optional[SimulationEngine] = None
        self.ai_engine = AIEngine(language=language)
        self._step_count = 0

    # ──────────────────────────────────────────
    #  OpenEnv Required APIs
    # ──────────────────────────────────────────

    def reset(self, custom_state: Optional[dict] = None) -> dict:
        """
        Reset environment to initial state.
        Returns: initial state dict
        """
        init_params = {**self.task_config["initial_state"], "currency": self.currency}
        if custom_state:
            init_params.update(custom_state)

        self.engine = SimulationEngine(init_params, seed=self.seed)
        self._step_count = 0
        self.ai_engine.conversation_history = []
        return self.engine.get_state()

    def step(self, action: dict) -> dict:
        """
        Execute one month of simulation with the given action.
        
        action: {
            "type": str,        # action type
            "params": dict,     # action parameters
        }
        
        Returns: {
            "state": dict,      # new state
            "prev_state": dict, # previous state
            "reward": float,    # step reward (0.0-1.0)
            "done": bool,
            "ai_insights": dict,
            "life_event": str,
        }
        """
        if self.engine is None:
            raise RuntimeError("Environment not initialised. Call reset() first.")

        result = self.engine.simulate_month(action)
        self._step_count += 1

        # Generate AI insights
        ai_insights = {}
        if self._step_count % 3 == 0:  # Every 3 steps to save API calls
            insights = self.ai_engine.generate_insights(
                result["state"], self.engine.get_history()
            )
            ai_insights = {"insights": insights}

        return {
            "state": result["state"],
            "prev_state": result["prev_state"],
            "reward": self._compute_step_reward(result["state"], result["prev_state"]),
            "done": result["done"] or self._step_count >= self.task_config["max_steps"],
            "ai_insights": ai_insights,
            "life_event": result["state"].get("life_event", "none"),
        }

    def state(self) -> dict:
        """Return current environment state."""
        if self.engine is None:
            raise RuntimeError("Environment not initialised. Call reset() first.")
        return self.engine.get_state()

    # ──────────────────────────────────────────
    #  Extended APIs
    # ──────────────────────────────────────────

    def history(self) -> list:
        """Return full simulation history."""
        if self.engine is None:
            return []
        return self.engine.get_history()

    def what_if(self, scenario: dict) -> list:
        """Run a what-if simulation without modifying actual state."""
        if self.engine is None:
            raise RuntimeError("Environment not initialised.")
        return self.engine.what_if(scenario)

    def ai_decide(self) -> tuple:
        """Let AI engine decide the next action."""
        return self.ai_engine.decide(self.state())

    def ai_chat(self, message: str) -> str:
        """Chat with the AI assistant about current finances."""
        return self.ai_engine.chat(message, self.state())

    def monthly_report(self) -> str:
        """Generate a monthly financial report."""
        return self.ai_engine.generate_monthly_report(
            self.state(), self.history()
        )

    def compare_strategies(self, strategies: list) -> dict:
        """
        Compare multiple financial strategies.
        strategies: [{"name": str, "action": dict, "months": int}]
        """
        results = {}
        for strategy in strategies:
            projections = self.what_if({
                "action": strategy["action"],
                "months": strategy.get("months", 12),
            })
            if projections:
                final = projections[-1]
                results[strategy["name"]] = {
                    "final_net_worth": final["net_worth"],
                    "final_savings": final["savings"],
                    "final_debt": final["debt"],
                    "final_health_score": final["health_score"],
                    "projections": projections,
                }
        return results

    def _compute_step_reward(self, state: dict, prev_state: dict) -> float:
        """Compute per-step reward (0.0 - 1.0)."""
        reward = 0.0

        # Net worth improvement (40%)
        nw_prev = prev_state.get("net_worth", 0)
        nw_curr = state.get("net_worth", 0)
        if nw_prev != 0:
            nw_change = (nw_curr - nw_prev) / abs(nw_prev)
            reward += max(0, min(0.40, nw_change * 2))

        # Health score (30%)
        health = state.get("health_score", 0)
        reward += (health / 100) * 0.30

        # Savings rate (20%)
        sr = state.get("savings_rate", 0)
        reward += min(sr / 0.30, 1.0) * 0.20

        # Debt reduction (10%)
        debt_prev = prev_state.get("debt", 0)
        debt_curr = state.get("debt", 0)
        if debt_prev > 0:
            debt_reduction = (debt_prev - debt_curr) / debt_prev
            reward += max(0, debt_reduction) * 0.10

        return round(min(1.0, max(0.0, reward)), 6)