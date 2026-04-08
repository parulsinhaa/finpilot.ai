"""
FinPilot AI — Multi-Channel Notification System
Channels: In-App, Email (SendGrid), SMS (Twilio), WhatsApp (Twilio/pywhatkit)
"""

import os
from datetime import datetime
from typing import Optional


# ─────────────────────────────────────────────
#  Email via SendGrid
# ─────────────────────────────────────────────

def send_email(to_email: str, subject: str, body_html: str,
               body_text: str = "") -> bool:
    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail

        sg = SendGridAPIClient(os.environ.get("SENDGRID_API_KEY", ""))
        message = Mail(
            from_email="noreply@finpilotai.com",
            to_emails=to_email,
            subject=subject,
            plain_text_content=body_text or _strip_html(body_html),
            html_content=_email_template(subject, body_html),
        )
        response = sg.send(message)
        return response.status_code in [200, 202]
    except Exception as e:
        print(f"[Notification] Email failed: {e}")
        return False


# ─────────────────────────────────────────────
#  SMS via Twilio
# ─────────────────────────────────────────────

def send_sms(to_phone: str, message: str) -> bool:
    try:
        from twilio.rest import Client
        client = Client(
            os.environ.get("TWILIO_ACCOUNT_SID", ""),
            os.environ.get("TWILIO_AUTH_TOKEN", "")
        )
        client.messages.create(
            body=message[:160],  # SMS char limit
            from_=os.environ.get("TWILIO_PHONE", "+1234567890"),
            to=to_phone
        )
        return True
    except Exception as e:
        print(f"[Notification] SMS failed: {e}")
        return False


# ─────────────────────────────────────────────
#  WhatsApp via Twilio WhatsApp API
# ─────────────────────────────────────────────

def send_whatsapp(to_phone: str, message: str) -> bool:
    try:
        from twilio.rest import Client
        client = Client(
            os.environ.get("TWILIO_ACCOUNT_SID", ""),
            os.environ.get("TWILIO_AUTH_TOKEN", "")
        )
        # Remove + for WhatsApp format
        wa_to = f"whatsapp:{to_phone}"
        wa_from = f"whatsapp:{os.environ.get('TWILIO_WHATSAPP_NUMBER', '+14155238886')}"
        client.messages.create(body=message, from_=wa_from, to=wa_to)
        return True
    except Exception as e:
        print(f"[Notification] WhatsApp failed: {e}")
        return False


# ─────────────────────────────────────────────
#  Notification Dispatcher
# ─────────────────────────────────────────────

class NotificationService:
    """Unified notification dispatcher for all channels."""

    def dispatch(self, user: dict, notification: dict) -> dict:
        """
        Send notification across enabled channels.
        user: {email, phone, email_notifications, sms_notifications,
               whatsapp_notifications, name}
        notification: {title, body, type, priority}
        """
        results = {}
        title = notification.get("title", "FinPilot AI")
        body = notification.get("body", "")
        notif_type = notification.get("type", "alert")

        # Email
        if user.get("email_notifications") and user.get("email"):
            html = _format_notification_html(title, body, notif_type)
            results["email"] = send_email(user["email"], title, html, body)

        # SMS
        if user.get("sms_notifications") and user.get("phone"):
            sms_text = f"FinPilot AI: {title}\n{body[:100]}"
            results["sms"] = send_sms(user["phone"], sms_text)

        # WhatsApp
        if user.get("whatsapp_notifications") and user.get("phone"):
            wa_text = (
                f"*FinPilot AI* — {title}\n\n"
                f"{body}\n\n"
                f"_Open the app to take action: finpilotai.com_"
            )
            results["whatsapp"] = send_whatsapp(user["phone"], wa_text)

        return results

    def notify_life_event(self, user: dict, event: str, impact: float):
        """Notify user of a significant life event."""
        event_messages = {
            "salary_increase":   ("Salary Increase Detected!", f"Your income increased. Impact: +{abs(impact):,.0f}"),
            "medical_emergency": ("Medical Emergency Alert", f"Emergency expense of {abs(impact):,.0f} recorded. Check your emergency fund."),
            "job_loss":          ("Employment Status Changed", "Job loss event simulated. FinPilot is recalculating your plan."),
            "market_crash":      ("Market Crash Alert", f"Portfolio impact: -{abs(impact):,.0f}. Reviewing your investment strategy."),
            "windfall":          ("Windfall Received!", f"Unexpected income of {abs(impact):,.0f}. AI is optimising allocation."),
        }
        if event in event_messages:
            title, body = event_messages[event]
            self.dispatch(user, {"title": title, "body": body, "type": "life_event"})

    def notify_goal_achieved(self, user: dict, goal_name: str):
        self.dispatch(user, {
            "title": f"Goal Achieved: {goal_name}!",
            "body": f"Congratulations! You have successfully reached your '{goal_name}' goal. Set a new one to keep growing.",
            "type": "achievement",
        })

    def notify_health_drop(self, user: dict, old_score: int, new_score: int):
        if old_score - new_score >= 10:
            self.dispatch(user, {
                "title": "Financial Health Score Dropped",
                "body": f"Your score dropped from {old_score} to {new_score}. Check the AI recommendations.",
                "type": "warning",
            })

    def send_monthly_report(self, user: dict, report_content: str, month: int):
        self.dispatch(user, {
            "title": f"Your Month {month} Financial Report is Ready",
            "body": f"Your personalised AI financial report for month {month} has been generated.\n\n{report_content[:200]}...",
            "type": "report",
        })

    def send_streak_reminder(self, user: dict, streak: int):
        self.dispatch(user, {
            "title": f"Streak Alert: {streak} Day Streak!",
            "body": f"You have maintained a {streak}-day financial discipline streak. Keep it up!",
            "type": "reminder",
        })


# ─────────────────────────────────────────────
#  Templates
# ─────────────────────────────────────────────

def _email_template(subject: str, body_html: str) -> str:
    return f"""
<!DOCTYPE html><html><head>
<meta charset="UTF-8">
<style>
  body {{ font-family: -apple-system, sans-serif; background: #FFF8F0; margin: 0; padding: 0; }}
  .container {{ max-width: 600px; margin: 20px auto; background: white; border-radius: 20px; overflow: hidden; box-shadow: 0 4px 30px rgba(255,107,157,0.15); }}
  .header {{ background: linear-gradient(135deg, #FF6B9D, #A78BFA); padding: 32px; text-align: center; }}
  .header h1 {{ color: white; font-size: 24px; margin: 0; font-weight: 700; }}
  .header p {{ color: rgba(255,255,255,0.8); margin: 8px 0 0; font-size: 14px; }}
  .body {{ padding: 32px; color: #1a1a2e; line-height: 1.7; }}
  .footer {{ background: #1a1a2e; color: rgba(255,255,255,0.4); padding: 20px; text-align: center; font-size: 12px; }}
  .cta {{ display: inline-block; background: linear-gradient(135deg, #FF6B9D, #A78BFA); color: white; padding: 12px 28px; border-radius: 50px; text-decoration: none; font-weight: 600; margin: 16px 0; }}
</style></head><body>
<div class="container">
  <div class="header">
    <h1>FinPilot AI</h1>
    <p>Your AI Financial Co-Pilot</p>
  </div>
  <div class="body">
    <h2 style="color:#FF6B9D;margin-top:0">{subject}</h2>
    {body_html}
    <br>
    <a href="https://finpilotai.com" class="cta">Open FinPilot AI</a>
  </div>
  <div class="footer">finpilotai.com — AI-Powered Financial Intelligence<br>
  Unsubscribe | Privacy Policy | Terms of Service</div>
</div>
</body></html>
"""


def _format_notification_html(title: str, body: str, notif_type: str) -> str:
    color_map = {
        "achievement": "#10b981",
        "warning": "#f59e0b",
        "life_event": "#A78BFA",
        "report": "#FF6B9D",
        "alert": "#ef4444",
        "reminder": "#3b82f6",
    }
    color = color_map.get(notif_type, "#FF6B9D")
    return (
        f'<div style="border-left:4px solid {color};padding-left:16px">'
        f'<p>{body}</p></div>'
    )


def _strip_html(html: str) -> str:
    import re
    return re.sub(r'<[^>]+>', '', html)


# Singleton
notification_service = NotificationService()