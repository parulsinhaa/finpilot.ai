"""
FinPilot AI — Main Streamlit Entry Point
"""

import streamlit as st
import os, sys

# Load .env for local dev
try:
    from dotenv import load_dotenv
    load_dotenv(override=False)
except ImportError:
    pass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(
    page_title="FinPilot AI — Your Financial Co-Pilot",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)


def load_css(theme: str = "pastel"):
    css_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "assets", "styles", "main.css",
    )
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    st.markdown(
        f'<script>document.body.setAttribute("data-theme","{theme}")</script>',
        unsafe_allow_html=True,
    )


DEFAULTS = {
    "logged_in": False, "user": None, "env": None, "current_state": None,
    "history": [], "chat_messages": [], "notifications": [],
    "theme": "pastel", "accent": "rose", "currency": "INR", "language": "English",
    "task": "wealth_building", "current_page": "landing", "plan": "free",
    "goals": [], "streak_days": 0, "unread_count": 0, "best_streak": 0,
    "last_insights": [], "wi_results": None, "current_report": None,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


def route():
    load_css(st.session_state.theme)
    if not st.session_state.logged_in:
        page = st.session_state.current_page
        if page == "login":
            from frontend.login import render_login; render_login()
        elif page == "signup":
            from frontend.login import render_signup; render_signup()
        else:
            from frontend.login import render_landing; render_landing()
    else:
        _render_auth()


def _render_auth():
    _sidebar()
    PAGES = {
        "dashboard":   ("frontend.dashboard",      "render_dashboard"),
        "calculators": ("frontend.calculators_ui", "render_calculators"),
        "ai_chat":     ("frontend.ai_chat",        "render_ai_chat"),
        "goals":       ("frontend.goals",          "render_goals"),
        "reports":     ("frontend.reports",        "render_reports"),
        "what_if":     ("frontend.what_if",        "render_what_if"),
        "settings":    ("frontend.settings",       "render_settings"),
    }
    page = st.session_state.current_page
    if page in PAGES:
        mod_path, fn = PAGES[page]
        mod = __import__(mod_path, fromlist=[fn])
        getattr(mod, fn)()
    else:
        from frontend.dashboard import render_dashboard; render_dashboard()


def _sidebar():
    with st.sidebar:
        # Logo
        logo_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "assets", "logo", "logo.svg",
        )
        if os.path.exists(logo_path):
            with open(logo_path) as f:
                svg = f.read()
            st.markdown(f'<div style="padding:0.25rem 0 1rem;">{svg}</div>',
                        unsafe_allow_html=True)
        else:
            st.markdown(
                '<div style="font-family:Bricolage Grotesque,sans-serif;font-size:1.4rem;'
                'font-weight:700;background:linear-gradient(135deg,#FF6B9D,#A78BFA);'
                '-webkit-background-clip:text;-webkit-text-fill-color:transparent;'
                'padding:0.5rem 0 1rem;text-align:center;">FinPilot AI</div>',
                unsafe_allow_html=True,
            )

        # User card
        user = st.session_state.user or {}
        plan = st.session_state.plan
        plan_c = {"free":"#8888aa","pro":"#A78BFA","premium":"#FF6B9D"}.get(plan,"#8888aa")
        init  = (user.get("name","U") or "U")[:1].upper()
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:0.6rem;padding:0.75rem;
                    background:rgba(255,107,157,0.06);border-radius:12px;
                    border:1px solid rgba(255,107,157,0.12);margin-bottom:0.9rem;">
          <div style="width:34px;height:34px;border-radius:50%;flex-shrink:0;
                      background:linear-gradient(135deg,#FF6B9D,#A78BFA);
                      display:flex;align-items:center;justify-content:center;
                      color:white;font-weight:700;font-size:0.88rem;">{init}</div>
          <div>
            <div style="font-weight:600;font-size:0.83rem;color:var(--text-primary,#1a1a2e);">{user.get('name','User')}</div>
            <div style="font-size:0.62rem;font-weight:700;color:{plan_c};text-transform:uppercase;">{plan}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Unread notifications
        unread = st.session_state.unread_count
        if unread:
            st.markdown(f"""
            <div style="background:rgba(255,107,157,0.08);border:1px solid rgba(255,107,157,0.2);
                        border-radius:9px;padding:0.35rem 0.7rem;margin-bottom:0.5rem;
                        display:flex;align-items:center;gap:0.4rem;font-size:0.73rem;color:#FF6B9D;">
              <span style="width:6px;height:6px;background:#FF6B9D;border-radius:50%;"></span>
              {unread} new notification{'s' if unread>1 else ''}
            </div>""", unsafe_allow_html=True)

        # Navigation buttons
        for page_key, label, icon in [
            ("dashboard",   "Dashboard",   "📊"),
            ("ai_chat",     "AI Advisor",  "🤖"),
            ("calculators", "Calculators", "🧮"),
            ("goals",       "Goals",       "🎯"),
            ("what_if",     "What-If",     "🔮"),
            ("reports",     "Reports",     "📋"),
            ("settings",    "Settings",    "⚙️"),
        ]:
            if st.button(f"{icon}  {label}", key=f"nav_{page_key}",
                         use_container_width=True):
                st.session_state.current_page = page_key
                st.rerun()

        st.markdown("<hr style='border:none;border-top:1px solid rgba(255,107,157,0.1);margin:0.7rem 0;'>",
                    unsafe_allow_html=True)

        # Health score mini ring
        hs = (st.session_state.current_state or {}).get("health_score", 0)
        color = "#10b981" if hs>=70 else "#f59e0b" if hs>=45 else "#ef4444"
        tier  = "Excellent" if hs>=80 else "Good" if hs>=60 else "Fair" if hs>=40 else "Start"
        dash  = hs/100*226.2
        st.markdown(f"""
        <div style="text-align:center;padding:0.4rem 0;">
          <svg width="76" height="76" viewBox="0 0 76 76">
            <circle cx="38" cy="38" r="32" fill="none" stroke="rgba(0,0,0,0.07)" stroke-width="6"/>
            <circle cx="38" cy="38" r="32" fill="none" stroke="{color}" stroke-width="6"
                    stroke-dasharray="{dash:.1f} 201.1" stroke-dashoffset="0"
                    stroke-linecap="round" transform="rotate(-90 38 38)"/>
            <text x="38" y="34" text-anchor="middle"
                  font-family="Bricolage Grotesque,sans-serif" font-size="14"
                  font-weight="700" fill="{color}">{hs}</text>
            <text x="38" y="45" text-anchor="middle"
                  font-family="DM Sans,sans-serif" font-size="7" fill="#8888aa">HEALTH</text>
          </svg>
          <div style="font-size:0.62rem;color:#8888aa;margin-top:-2px;">{tier}</div>
        </div>
        """, unsafe_allow_html=True)

        # Streak
        streak = st.session_state.streak_days
        if streak > 0:
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:0.4rem;padding:0.45rem 0.7rem;
                        background:rgba(255,107,157,0.07);border-radius:9px;margin-top:0.4rem;">
              <span>🔥</span>
              <span style="font-weight:700;color:#FF6B9D;font-size:0.95rem;">{streak}</span>
              <span style="font-size:0.7rem;color:#8888aa;">day streak</span>
            </div>""", unsafe_allow_html=True)

        # Quick pickers
        st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            nt = st.selectbox("", ["pastel","dark","minimal","ocean"],
                    index=["pastel","dark","minimal","ocean"].index(st.session_state.theme),
                    key="_th", label_visibility="collapsed")
            if nt != st.session_state.theme:
                st.session_state.theme = nt; st.rerun()
        with c2:
            nc = st.selectbox("", ["INR","USD","EUR","GBP","AED"],
                    index=["INR","USD","EUR","GBP","AED"].index(st.session_state.currency),
                    key="_cu", label_visibility="collapsed")
            if nc != st.session_state.currency:
                st.session_state.currency = nc; st.rerun()

        if st.button("Logout", use_container_width=True, key="nav_logout"):
            for k, v in DEFAULTS.items():
                st.session_state[k] = v
            st.rerun()


if __name__ == "__main__":
    route()