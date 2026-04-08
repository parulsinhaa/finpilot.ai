"""
FinPilot AI — AI Decision Engine
Uses OpenAI GPT-4o to analyse financial state and produce
structured, explainable recommendations in multiple languages.
"""

import os
import json
from typing import Optional
from openai import OpenAI


LANGUAGE_PROMPTS = {
    "English": "Respond entirely in English.",
    "Hindi":   "हिंदी में जवाब दें। Use Devanagari script.",
    "Spanish": "Responde completamente en español.",
    "French":  "Réponds entièrement en français.",
}

SYSTEM_PROMPT = """You are FinPilot AI, an expert financial advisor and decision-making engine.
You analyse a person's complete financial state (income, expenses, savings, debt, investments,
life events) and output structured, explainable financial recommendations.

Your output MUST always be valid JSON with this exact schema:
{{
  "action": {{
    "type": "save|invest_sip|repay_debt|adjust_expenses|build_emergency_fund|withdraw_investment|take_loan",
    "params": {{...}},
    "confidence": 0.0-1.0
  }},
  "reasoning": "detailed explanation of why this action is recommended",
  "impact": {{
    "net_worth_change": float,
    "savings_change": float,
    "debt_change": float,
    "health_score_change": int,
    "timeline_months": int
  }},
  "risk_level": "low|medium|high",
  "alternatives": [
    {{"action_type": "...", "summary": "brief alternative explanation"}}
  ],
  "warning": "optional warning if life event detected",
  "insight": "one-line key insight for the user"
}}

Always be specific with amounts. Base all decisions on the actual numbers provided.
Never recommend withdrawing all savings or taking on debt unnecessarily.
{language_instruction}
"""


class AIEngine:
    """Wraps OpenAI API to produce financial decisions from environment state."""

    def __init__(self, language: str = "English"):
        self.language = language
        self.client = None
        self._init_client()
        self.conversation_history = []

    def _init_client(self):
        api_key = os.environ.get("OPENAI_API_KEY", "")
        base_url = os.environ.get("API_BASE_URL", "https://api.openai.com/v1")
        model = os.environ.get("MODEL_NAME", "gpt-4o")

        if api_key:
            self.client = OpenAI(api_key=api_key, base_url=base_url)
            self.model = model
        else:
            self.client = None
            self.model = model

    def decide(self, state: dict) -> tuple[dict, str]:
        """
        Analyse financial state and return (action_dict, reasoning_str).
        Falls back to rule-based engine if OpenAI is unavailable.
        """
        if self.client is None:
            return self._rule_based_decide(state)

        prompt = self._build_prompt(state)
        lang_instruction = LANGUAGE_PROMPTS.get(self.language, LANGUAGE_PROMPTS["English"])

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system",
                     "content": SYSTEM_PROMPT.format(language_instruction=lang_instruction)},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000,
                response_format={"type": "json_object"},
            )

            raw = response.choices[0].message.content
            parsed = json.loads(raw)
            action = parsed.get("action", {})
            reasoning = parsed.get("reasoning", "")
            return action, reasoning

        except Exception as e:
            # Graceful fallback
            return self._rule_based_decide(state)

    def chat(self, user_message: str, state: dict) -> str:
        """
        Conversational AI assistant — user asks free-form financial questions.
        """
        if self.client is None:
            return self._rule_based_chat(user_message, state)

        lang_instruction = LANGUAGE_PROMPTS.get(self.language, LANGUAGE_PROMPTS["English"])

        # Build context from state
        context = (
            f"Current financial state: Income={state.get('income')}, "
            f"Savings={state.get('savings')}, Debt={state.get('debt')}, "
            f"Investments={state.get('investments')}, "
            f"Net Worth={state.get('net_worth')}, "
            f"Health Score={state.get('health_score')}/100, "
            f"Month={state.get('month')}"
        )

        self.conversation_history.append({
            "role": "user",
            "content": f"Context: {context}\n\nUser Question: {user_message}"
        })

        # Keep last 10 messages for context
        messages = [
            {"role": "system",
             "content": f"You are FinPilot AI, a friendly expert financial advisor. "
                        f"Answer questions about the user's finances clearly and practically. "
                        f"{lang_instruction}"}
        ] + self.conversation_history[-10:]

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.6,
                max_tokens=600,
            )
            reply = response.choices[0].message.content
            self.conversation_history.append({"role": "assistant", "content": reply})
            return reply

        except Exception:
            return self._rule_based_chat(user_message, state)

    def generate_insights(self, state: dict, history: list) -> list:
        """Generate 3-5 AI insights based on current state and history."""
        if self.client is None:
            return self._rule_based_insights(state)

        prompt = (
            f"Based on this financial data, generate 4 specific, actionable insights.\n"
            f"State: {json.dumps(state, default=str)}\n"
            f"History length: {len(history)} months\n"
            f"Return JSON: {{\"insights\": [{{\"title\": str, \"detail\": str, "
            f"\"type\": \"positive|warning|neutral|action\", \"priority\": int}}]}}"
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system",
                     "content": f"You are FinPilot AI. Generate financial insights. "
                                f"{LANGUAGE_PROMPTS.get(self.language, '')}"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=800,
                response_format={"type": "json_object"},
            )
            parsed = json.loads(response.choices[0].message.content)
            return parsed.get("insights", [])

        except Exception:
            return self._rule_based_insights(state)

    def generate_monthly_report(self, state: dict, history: list) -> str:
        """Generate a comprehensive monthly financial report."""
        if self.client is None:
            return self._rule_based_report(state)

        prompt = (
            f"Generate a comprehensive monthly financial report for Month {state.get('month')}.\n"
            f"State: {json.dumps(state, default=str)}\n"
            f"Write in a professional but friendly tone. Cover:\n"
            f"1. Executive Summary\n2. Income & Expenses Analysis\n"
            f"3. Net Worth Progress\n4. Debt Status\n5. Investment Performance\n"
            f"6. Goals Progress\n7. Recommendations for Next Month\n"
            f"8. Financial Health Score breakdown"
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system",
                     "content": f"You are FinPilot AI. Write a detailed monthly financial report. "
                                f"{LANGUAGE_PROMPTS.get(self.language, '')}"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=2000,
            )
            return response.choices[0].message.content

        except Exception:
            return self._rule_based_report(state)

    # ──────────────────────────────────────────
    #  Rule-based fallback (no API key needed)
    # ──────────────────────────────────────────

    def _rule_based_decide(self, state: dict) -> tuple[dict, str]:
        """Smart rule-based financial decision engine."""
        income = state.get("income", 1)
        savings = state.get("savings", 0)
        debt = state.get("debt", 0)
        investments = state.get("investments", 0)
        ef = state.get("emergency_fund", 0)
        monthly_expenses = state.get("monthly_expenses", income * 0.65)
        surplus = state.get("monthly_surplus", 0)
        life_event = state.get("life_event", "none")
        health = state.get("health_score", 50)

        ef_months = ef / max(monthly_expenses, 1)

        # Priority 1: Emergency after life event
        if life_event in ["medical_emergency", "job_loss"]:
            return (
                {"type": "build_emergency_fund", "params": {"amount": min(surplus * 0.8, surplus)}, "confidence": 0.9},
                f"Life event '{life_event}' detected. Prioritising emergency fund rebuild."
            )

        # Priority 2: Emergency fund < 3 months
        if ef_months < 3 and surplus > 0:
            amount = min(surplus * 0.6, monthly_expenses)
            return (
                {"type": "build_emergency_fund", "params": {"amount": round(amount, 2)}, "confidence": 0.88},
                f"Emergency fund covers only {ef_months:.1f} months. Target: 6 months. Adding {amount:.0f}."
            )

        # Priority 3: High-interest debt
        debt_rate = state.get("debt_interest_rate", 0)
        if debt > 0 and debt_rate > 14 and surplus > 0:
            payment = min(surplus * 0.5, debt)
            return (
                {"type": "repay_debt", "params": {"amount": round(payment, 2)}, "confidence": 0.85},
                f"High-interest debt at {debt_rate}%. Extra payment of {payment:.0f} saves significantly in interest."
            )

        # Priority 4: No investments
        if investments < income * 3 and surplus > 5000:
            sip = min(surplus * 0.3, income * 0.15)
            return (
                {"type": "invest_sip", "params": {"amount": round(sip, 2), "fund_type": "equity_index"}, "confidence": 0.82},
                f"Investment portfolio is thin. Starting SIP of {sip:.0f}/month in equity index funds."
            )

        # Priority 5: Moderate debt + good emergency fund
        if debt > income * 6 and ef_months >= 3:
            payment = min(surplus * 0.4, debt * 0.05)
            return (
                {"type": "repay_debt", "params": {"amount": round(payment, 2)}, "confidence": 0.78},
                f"Debt is {debt/income:.1f}x monthly income. Aggressive paydown recommended."
            )

        # Default: Balanced save + invest
        save_amount = round(surplus * 0.4, 2)
        return (
            {"type": "save", "params": {"amount": save_amount}, "confidence": 0.70},
            f"Financial position is stable. Saving {save_amount:.0f} from monthly surplus of {surplus:.0f}."
        )

    def _rule_based_insights(self, state: dict) -> list:
        insights = []
        income = state.get("income", 1)
        savings_rate = state.get("savings_rate", 0)
        ef_months = state.get("emergency_fund_months", 0)
        health = state.get("health_score", 50)
        debt = state.get("debt", 0)

        if savings_rate < 0.10:
            insights.append({"title": "Low Savings Rate",
                              "detail": f"You're saving {savings_rate*100:.1f}%. Target 20%+ for financial security.",
                              "type": "warning", "priority": 1})
        if ef_months < 3:
            insights.append({"title": "Emergency Fund Insufficient",
                              "detail": f"Only {ef_months:.1f} months covered. Build to 6 months.",
                              "type": "action", "priority": 2})
        if health >= 80:
            insights.append({"title": "Excellent Financial Health",
                              "detail": f"Score of {health}/100 puts you in the top tier. Keep it up!",
                              "type": "positive", "priority": 3})
        if debt == 0:
            insights.append({"title": "Debt Free",
                              "detail": "No outstanding debt. Redirect debt payments to investments.",
                              "type": "positive", "priority": 1})

        return insights[:4]

    def _rule_based_chat(self, question: str, state: dict) -> str:
        q = question.lower()
        income = state.get("income", 0)
        savings = state.get("savings", 0)
        debt = state.get("debt", 0)
        health = state.get("health_score", 0)

        if any(w in q for w in ["save", "saving", "savings"]):
            return (f"Your current savings are {savings:,.0f} with a savings rate of "
                    f"{state.get('savings_rate', 0)*100:.1f}%. "
                    f"Financial experts recommend saving at least 20% of income. "
                    f"Based on your income of {income:,.0f}, that would be {income*0.20:,.0f}/month.")
        elif any(w in q for w in ["debt", "loan", "emi"]):
            return (f"Your outstanding debt is {debt:,.0f}. "
                    f"The debt-to-income ratio guideline suggests keeping monthly debt payments "
                    f"below 35% of income. Prioritise high-interest debt first using the "
                    f"avalanche method to minimise total interest paid.")
        elif any(w in q for w in ["invest", "sip", "mutual fund"]):
            return (f"Your current investments are {state.get('investments', 0):,.0f}. "
                    f"For long-term wealth building, a monthly SIP in equity index funds "
                    f"historically returns 12-15% annually. Starting with "
                    f"{min(income*0.15, 10000):,.0f}/month would be a good target.")
        else:
            return (f"Your financial health score is {health}/100. "
                    f"Net worth: {state.get('net_worth', 0):,.0f}. "
                    f"Ask me anything about your savings, investments, debt, or financial goals!")

    def _rule_based_report(self, state: dict) -> str:
        return (
            f"## FinPilot AI — Monthly Financial Report\n"
            f"**Month {state.get('month', 1)}**\n\n"
            f"### Summary\n"
            f"- Net Worth: {state.get('net_worth', 0):,.0f} {state.get('currency', 'INR')}\n"
            f"- Health Score: {state.get('health_score', 0)}/100\n"
            f"- Monthly Savings Rate: {state.get('savings_rate', 0)*100:.1f}%\n\n"
            f"### Key Metrics\n"
            f"- Income: {state.get('income', 0):,.0f}\n"
            f"- Expenses: {state.get('monthly_expenses', 0):,.0f}\n"
            f"- Surplus: {state.get('monthly_surplus', 0):,.0f}\n"
            f"- Savings: {state.get('savings', 0):,.0f}\n"
            f"- Investments: {state.get('investments', 0):,.0f}\n"
            f"- Debt: {state.get('debt', 0):,.0f}\n\n"
            f"*Report generated by FinPilot AI Rule Engine (API key not configured)*"
        )

    def _build_prompt(self, state: dict) -> str:
        return (
            f"Analyse this financial state and recommend the optimal action:\n\n"
            f"Month: {state.get('month', 0)}\n"
            f"Income: {state.get('income', 0):,.0f} {state.get('currency', 'INR')}\n"
            f"Monthly Expenses: {state.get('monthly_expenses', 0):,.0f}\n"
            f"Monthly Surplus: {state.get('monthly_surplus', 0):,.0f}\n"
            f"Savings: {state.get('savings', 0):,.0f}\n"
            f"Debt: {state.get('debt', 0):,.0f} (rate: {state.get('debt_interest_rate', 0)}%)\n"
            f"Investments: {state.get('investments', 0):,.0f}\n"
            f"Emergency Fund: {state.get('emergency_fund', 0):,.0f} "
            f"({state.get('emergency_fund_months', 0):.1f} months)\n"
            f"Net Worth: {state.get('net_worth', 0):,.0f}\n"
            f"Health Score: {state.get('health_score', 0)}/100\n"
            f"Life Event This Month: {state.get('life_event', 'none')}\n"
            f"Savings Rate: {state.get('savings_rate', 0)*100:.1f}%\n"
            f"Expenses breakdown: {json.dumps(state.get('expenses', {}))}\n\n"
            f"What is the single most impactful financial action to take this month? "
            f"Respond with valid JSON only."
        )