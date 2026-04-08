"""
FinPilot AI — Payments (PayPal)
PayPal email: parulsinhaa19@gmail.com
"""

import os
import json
from datetime import datetime


PLAN_PRICES = {
    "pro":     {"monthly": 99,  "annual": 990,  "currency": "INR"},
    "premium": {"monthly": 299, "annual": 2990, "currency": "INR"},
}

PAYPAL_RECEIVER = os.environ.get("PAYPAL_EMAIL", "parulsinhaa19@gmail.com")


class PaymentService:
    """Handles PayPal payment processing for subscriptions."""

    def __init__(self):
        self._init_paypal()

    def _init_paypal(self):
        """Initialise PayPal SDK."""
        try:
            import paypalrestsdk
            paypalrestsdk.configure({
                "mode": os.environ.get("PAYPAL_MODE", "sandbox"),
                "client_id": os.environ.get("PAYPAL_CLIENT_ID", ""),
                "client_secret": os.environ.get("PAYPAL_CLIENT_SECRET", ""),
            })
            self.paypal = paypalrestsdk
            self.available = bool(os.environ.get("PAYPAL_CLIENT_ID"))
        except Exception:
            self.paypal = None
            self.available = False

    def create_subscription_payment(self, plan: str, billing_cycle: str,
                                     user_email: str,
                                     return_url: str = "https://finpilotai.com/payment/success",
                                     cancel_url: str = "https://finpilotai.com/payment/cancel"
                                     ) -> dict:
        """Create a PayPal payment for a subscription plan."""
        if plan not in PLAN_PRICES:
            return {"success": False, "error": "Invalid plan"}

        pricing = PLAN_PRICES[plan]
        amount = pricing["annual"] if billing_cycle == "annual" else pricing["monthly"]
        description = f"FinPilot AI {plan.title()} Plan — {billing_cycle.title()}"

        if not self.available:
            # Mock response for dev/testing
            return {
                "success": True,
                "payment_id": f"MOCK_{plan}_{datetime.utcnow().timestamp():.0f}",
                "approval_url": f"https://finpilotai.com/mock-payment?plan={plan}&amount={amount}",
                "mock": True,
            }

        try:
            payment = self.paypal.Payment({
                "intent": "sale",
                "payer": {"payment_method": "paypal"},
                "redirect_urls": {
                    "return_url": return_url,
                    "cancel_url": cancel_url,
                },
                "transactions": [{
                    "amount": {
                        "total": str(amount),
                        "currency": "USD",  # PayPal standard
                    },
                    "description": description,
                    "payee": {"email": PAYPAL_RECEIVER},
                    "item_list": {
                        "items": [{
                            "name": description,
                            "price": str(amount),
                            "currency": "USD",
                            "quantity": "1",
                        }]
                    },
                }],
            })

            if payment.create():
                approval_url = next(
                    (l["href"] for l in payment.links if l["rel"] == "approval_url"), ""
                )
                return {
                    "success": True,
                    "payment_id": payment.id,
                    "approval_url": approval_url,
                }
            else:
                return {"success": False, "error": str(payment.error)}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def execute_payment(self, payment_id: str, payer_id: str) -> dict:
        """Execute a PayPal payment after user approval."""
        if not self.available:
            return {"success": True, "mock": True, "payment_id": payment_id}

        try:
            payment = self.paypal.Payment.find(payment_id)
            if payment.execute({"payer_id": payer_id}):
                return {
                    "success": True,
                    "payment_id": payment_id,
                    "amount": payment.transactions[0].amount.total,
                    "currency": payment.transactions[0].amount.currency,
                    "state": payment.state,
                }
            else:
                return {"success": False, "error": "Payment execution failed"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_payment_link(self, plan: str) -> str:
        """Get a quick PayPal.me payment link."""
        amounts = {"pro": 99, "premium": 299}
        amount = amounts.get(plan, 99)
        return f"https://paypal.me/{PAYPAL_RECEIVER.split('@')[0]}/{amount}"


# Singleton
payment_service = PaymentService()