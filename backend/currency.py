"""
FinPilot AI — Currency Service
Supports INR, USD, EUR, GBP, AED with live + cached rates.
"""

import os
import httpx
from datetime import datetime, timedelta

# Hardcoded fallback rates (INR base)
FALLBACK_RATES = {
    "INR": 1.0,
    "USD": 0.01201,
    "EUR": 0.01105,
    "GBP": 0.00946,
    "AED": 0.04409,
    "JPY": 1.805,
    "SGD": 0.01613,
    "CAD": 0.01635,
    "AUD": 0.01843,
    "CHF": 0.01080,
}

CURRENCY_SYMBOLS = {
    "INR": "₹",
    "USD": "$",
    "EUR": "€",
    "GBP": "£",
    "AED": "د.إ",
    "JPY": "¥",
    "SGD": "S$",
    "CAD": "C$",
    "AUD": "A$",
    "CHF": "Fr",
}

CURRENCY_NAMES = {
    "INR": "Indian Rupee",
    "USD": "US Dollar",
    "EUR": "Euro",
    "GBP": "British Pound",
    "AED": "UAE Dirham",
}

_rate_cache = {"rates": FALLBACK_RATES.copy(), "updated": datetime.utcnow()}


def get_rates(force_refresh: bool = False) -> dict:
    """Get exchange rates with 1-hour caching."""
    global _rate_cache

    age = datetime.utcnow() - _rate_cache["updated"]
    if not force_refresh and age < timedelta(hours=1):
        return _rate_cache["rates"]

    api_key = os.environ.get("EXCHANGE_RATE_API_KEY", "")
    if api_key:
        try:
            resp = httpx.get(
                f"https://v6.exchangerate-api.com/v6/{api_key}/base/INR",
                timeout=5.0
            )
            if resp.status_code == 200:
                data = resp.json()
                _rate_cache = {
                    "rates": data.get("conversion_rates", FALLBACK_RATES),
                    "updated": datetime.utcnow()
                }
                return _rate_cache["rates"]
        except Exception:
            pass

    return FALLBACK_RATES


def convert(amount: float, from_currency: str, to_currency: str) -> float:
    """Convert amount between currencies via INR base."""
    if from_currency == to_currency:
        return round(amount, 2)

    rates = get_rates()
    from_rate = rates.get(from_currency, 1.0)
    to_rate = rates.get(to_currency, 1.0)

    # Convert to INR then to target
    inr_amount = amount / from_rate
    result = inr_amount * to_rate
    return round(result, 2)


def format_currency(amount: float, currency: str = "INR",
                     compact: bool = False) -> str:
    """Format amount with currency symbol and Indian/standard notation."""
    symbol = CURRENCY_SYMBOLS.get(currency, currency)

    if compact:
        if currency == "INR":
            if amount >= 1e7: return f"{symbol}{amount/1e7:.1f}Cr"
            if amount >= 1e5: return f"{symbol}{amount/1e5:.1f}L"
            if amount >= 1e3: return f"{symbol}{amount/1e3:.1f}K"
        else:
            if amount >= 1e6: return f"{symbol}{amount/1e6:.1f}M"
            if amount >= 1e3: return f"{symbol}{amount/1e3:.1f}K"
        return f"{symbol}{amount:.0f}"

    if currency == "INR":
        # Indian number format: 1,00,00,000
        try:
            import babel.numbers
            return babel.numbers.format_currency(amount, currency, locale="en_IN")
        except Exception:
            pass

    return f"{symbol}{amount:,.2f}"


def convert_state(state: dict, to_currency: str) -> dict:
    """Convert all monetary values in state to target currency."""
    from_currency = state.get("currency", "INR")
    if from_currency == to_currency:
        return state

    monetary_keys = [
        "income", "savings", "debt", "investments", "emergency_fund",
        "net_worth", "monthly_expenses", "monthly_surplus",
        "monthly_debt_payment", "sip_amount", "initial_net_worth",
        "emergency_fund_required", "life_event_impact",
    ]

    converted = dict(state)
    for key in monetary_keys:
        if key in converted and isinstance(converted[key], (int, float)):
            converted[key] = convert(converted[key], from_currency, to_currency)

    # Convert expenses dict
    if "expenses" in converted:
        converted["expenses"] = {
            cat: convert(val, from_currency, to_currency)
            for cat, val in converted["expenses"].items()
        }

    converted["currency"] = to_currency
    return converted