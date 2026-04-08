"""
FinPilot AI — Login / Signup UI
Beautiful pastel auth screens with global phone + country code support.
"""

import streamlit as st
import hashlib, time
from datetime import datetime

COUNTRY_CODES = [
    "+91 IN — India", "+1 US — United States", "+44 UK — United Kingdom",
    "+971 AE — UAE", "+33 FR — France", "+49 DE — Germany",
    "+81 JP — Japan", "+86 CN — China", "+55 BR — Brazil",
    "+61 AU — Australia", "+65 SG — Singapore", "+27 ZA — South Africa",
    "+7 RU — Russia", "+82 KR — South Korea", "+52 MX — Mexico",
    "+39 IT — Italy", "+34 ES — Spain", "+31 NL — Netherlands",
    "+46 SE — Sweden", "+47 NO — Norway", "+45 DK — Denmark",
    "+41 CH — Switzerland", "+43 AT — Austria", "+32 BE — Belgium",
    "+48 PL — Poland", "+90 TR — Turkey", "+62 ID — Indonesia",
    "+63 PH — Philippines", "+66 TH — Thailand", "+60 MY — Malaysia",
    "+92 PK — Pakistan", "+880 BD — Bangladesh", "+94 LK — Sri Lanka",
    "+977 NP — Nepal", "+20 EG — Egypt", "+234 NG — Nigeria",
    "+254 KE — Kenya", "+1 CA — Canada", "+64 NZ — New Zealand",
    "+54 AR — Argentina", "+56 CL — Chile", "+51 PE — Peru",
    "+57 CO — Colombia", "+58 VE — Venezuela",
]


def render_landing():
    """Landing page with hero + CTA to login/signup."""
    _inject_auth_styles()

    st.markdown("""
    <div class="auth-hero">
      <div class="auth-hero-content">
        <div class="auth-badge">
          <span class="auth-badge-dot"></span>
          AI-Powered Financial Intelligence
        </div>
        <h1 class="auth-hero-title">
          Your money,<br>
          <span class="auth-gradient-text">finally working for you</span>
        </h1>
        <p class="auth-hero-sub">
          FinPilot AI simulates your complete financial life — income, savings, debt,
          investments — and delivers intelligent, explainable decisions at every step.
        </p>
        <div class="auth-hero-stats">
          <div class="auth-stat"><span class="auth-stat-val">3×</span><span class="auth-stat-lbl">Wealth Growth</span></div>
          <div class="auth-stat"><span class="auth-stat-val">AI</span><span class="auth-stat-lbl">Decision Engine</span></div>
          <div class="auth-stat"><span class="auth-stat-val">5</span><span class="auth-stat-lbl">Currencies</span></div>
          <div class="auth-stat"><span class="auth-stat-val">4</span><span class="auth-stat-lbl">Languages</span></div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Get Started Free", use_container_width=True, type="primary"):
                st.session_state.current_page = "signup"
                st.rerun()
        with c2:
            if st.button("Sign In", use_container_width=True):
                st.session_state.current_page = "login"
                st.rerun()

    # Feature pills
    st.markdown("""
    <div style="display:flex;flex-wrap:wrap;gap:0.5rem;justify-content:center;
                margin-top:2rem;padding:0 2rem;">
      <span class="auth-feature-pill">EMI Calculator</span>
      <span class="auth-feature-pill">SIP Projections</span>
      <span class="auth-feature-pill">AI Advisor</span>
      <span class="auth-feature-pill">Life Event Simulation</span>
      <span class="auth-feature-pill">What-If Engine</span>
      <span class="auth-feature-pill">Goal Tracking</span>
      <span class="auth-feature-pill">Monthly Reports</span>
      <span class="auth-feature-pill">Multi-Currency</span>
    </div>
    """, unsafe_allow_html=True)


def render_login():
    """Login form."""
    _inject_auth_styles()
    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        _render_auth_card(mode="login")


def render_signup():
    """Signup form."""
    _inject_auth_styles()
    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        _render_auth_card(mode="signup")


def _render_auth_card(mode: str):
    st.markdown("""
    <div style="margin-top:4rem;">
      <div style="text-align:center;margin-bottom:1.5rem;">
        <div style="font-family:'Bricolage Grotesque',sans-serif;font-size:2rem;
                    font-weight:700;background:linear-gradient(135deg,#FF6B9D,#A78BFA);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                    margin-bottom:0.25rem;">FinPilot AI</div>
        <div style="color:#8888aa;font-size:0.85rem;">Your AI Financial Co-Pilot</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Tab switcher
    tab_login, tab_signup = st.tabs(["Sign In", "Create Account"])

    # ── LOGIN ──
    with tab_login:
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        with st.form("login_form"):
            country = st.selectbox("Country Code", COUNTRY_CODES,
                                    index=0, key="login_country")
            phone = st.text_input("Phone Number", placeholder="98765 43210",
                                   key="login_phone")
            password = st.text_input("Password", type="password",
                                      key="login_password")

            col1, col2 = st.columns(2)
            with col1:
                currency = st.selectbox("Currency", ["INR","USD","EUR","GBP","AED"],
                                         key="login_currency")
            with col2:
                language = st.selectbox("Language", ["English","Hindi","Spanish","French"],
                                         key="login_language")

            remember = st.checkbox("Remember me for 7 days")
            submitted = st.form_submit_button("Sign In to FinPilot",
                                               use_container_width=True, type="primary")

        if submitted:
            if phone and password:
                _do_login(phone, password, currency, language,
                          country.split(" ")[0])
            else:
                st.error("Please enter phone number and password.")

        st.markdown("<hr style='border:none;border-top:1px solid rgba(255,107,157,0.12);margin:1rem 0;'>",
                    unsafe_allow_html=True)
        st.markdown(
            "<div style='text-align:center;font-size:0.8rem;color:#8888aa;'>"
            "No account? "
            "</div>", unsafe_allow_html=True
        )
        if st.button("Create Free Account", use_container_width=True):
            st.session_state.current_page = "signup"
            st.rerun()

    # ── SIGNUP ──
    with tab_signup:
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        with st.form("signup_form"):
            name = st.text_input("Full Name", placeholder="Parul Sinha",
                                  key="signup_name")
            email = st.text_input("Email Address", placeholder="you@example.com",
                                   key="signup_email")
            country = st.selectbox("Country Code", COUNTRY_CODES,
                                    index=0, key="signup_country")
            phone = st.text_input("Phone Number", placeholder="98765 43210",
                                   key="signup_phone")
            col1, col2 = st.columns(2)
            with col1:
                password = st.text_input("Password", type="password",
                                          key="signup_password")
            with col2:
                confirm = st.text_input("Confirm Password", type="password",
                                         key="signup_confirm")
            col3, col4 = st.columns(2)
            with col3:
                currency = st.selectbox("Currency", ["INR","USD","EUR","GBP","AED"],
                                         key="signup_currency")
            with col4:
                language = st.selectbox("Language", ["English","Hindi","Spanish","French"],
                                         key="signup_language")
            task = st.selectbox("Starting Goal", [
                "wealth_building — Build serious wealth",
                "debt_payoff — Pay off debt fast",
                "budget_balance — Master my budget",
            ], key="signup_task")

            terms = st.checkbox("I agree to Terms of Service and Privacy Policy")
            submitted = st.form_submit_button("Create My Account",
                                               use_container_width=True, type="primary")

        if submitted:
            if not all([name, phone, password, email]):
                st.error("Please fill in all required fields.")
            elif password != confirm:
                st.error("Passwords do not match.")
            elif not terms:
                st.warning("Please accept the Terms of Service.")
            else:
                task_key = task.split(" — ")[0]
                _do_signup(name, email, phone, password, currency,
                           language, task_key, country.split(" ")[0])

    # Back to landing
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    if st.button("Back to Home"):
        st.session_state.current_page = "landing"
        st.rerun()


def _do_login(phone, password, currency, language, country_code):
    """Simulate login (replace with real DB auth in production)."""
    with st.spinner("Signing in..."):
        time.sleep(0.5)

    # In production: query DB, verify password hash
    # For demo: accept any credentials
    st.session_state.logged_in = True
    st.session_state.user = {
        "name": "Demo User",
        "phone": phone,
        "country_code": country_code,
        "email": "",
        "plan": "pro",
    }
    st.session_state.currency = currency
    st.session_state.language = language
    st.session_state.plan = "pro"
    st.session_state.current_page = "dashboard"

    # Init environment
    _init_env(language, currency, "wealth_building")
    st.success("Welcome back to FinPilot AI!")
    time.sleep(0.3)
    st.rerun()


def _do_signup(name, email, phone, password, currency, language, task, country_code):
    """Simulate signup."""
    with st.spinner("Creating your account..."):
        time.sleep(0.8)

    st.session_state.logged_in = True
    st.session_state.user = {
        "name": name,
        "phone": phone,
        "email": email,
        "country_code": country_code,
        "plan": "free",
    }
    st.session_state.currency = currency
    st.session_state.language = language
    st.session_state.plan = "free"
    st.session_state.task = task
    st.session_state.current_page = "dashboard"

    _init_env(language, currency, task)
    st.success(f"Welcome to FinPilot AI, {name}!")
    time.sleep(0.3)
    st.rerun()


def _init_env(language, currency, task):
    """Initialise the FinPilot environment for this session."""
    try:
        from app.environment import FinPilotEnv
        env = FinPilotEnv(task=task, language=language, currency=currency)
        initial_state = env.reset()
        st.session_state.env = env
        st.session_state.current_state = initial_state
        st.session_state.history = []
        st.session_state.notifications = [
            {"title": "Welcome to FinPilot AI!", "body": "Your financial simulation is ready. Press 'Next Month' to begin.",
             "type": "info", "read": False},
            {"title": "AI Advisor Activated", "body": "Your AI financial advisor is analysing your profile.",
             "type": "ai", "read": False},
        ]
        st.session_state.unread_count = 2
    except Exception as e:
        st.error(f"Environment init error: {e}")


def _inject_auth_styles():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@400;700&family=DM+Sans:wght@300;400;500&display=swap');
    #MainMenu,footer,header{visibility:hidden}
    .stDeployButton{display:none}
    .main .block-container{padding:0 !important;max-width:100% !important}

    .auth-hero {
      width:100%;padding:5rem 2rem 2rem;text-align:center;
      background:radial-gradient(ellipse 80% 60% at 50% 0%,rgba(255,107,157,0.12),transparent 60%),
                 radial-gradient(ellipse 60% 80% at 80% 50%,rgba(167,139,250,0.10),transparent 60%),
                 #FFF8F0;
    }
    .auth-badge {
      display:inline-flex;align-items:center;gap:0.5rem;
      background:rgba(255,107,157,0.1);border:1px solid rgba(255,107,157,0.25);
      color:#FF6B9D;padding:0.35rem 1rem;border-radius:50px;
      font-size:0.78rem;font-weight:500;margin-bottom:1.5rem;
    }
    .auth-badge-dot {
      width:6px;height:6px;background:#FF6B9D;border-radius:50%;
      animation:pulse 2s infinite;
    }
    @keyframes pulse{0%,100%{opacity:1}50%{opacity:0.4}}
    .auth-hero-title {
      font-family:'Bricolage Grotesque',sans-serif;
      font-size:clamp(2.5rem,6vw,4.5rem);font-weight:700;
      line-height:1.05;letter-spacing:-0.04em;color:#1a1a2e;margin-bottom:1rem;
    }
    .auth-gradient-text {
      background:linear-gradient(135deg,#FF6B9D,#A78BFA,#FF8C6B);
      -webkit-background-clip:text;-webkit-text-fill-color:transparent;
    }
    .auth-hero-sub {
      color:#4a4a6a;font-size:1.05rem;max-width:560px;
      margin:0 auto 2rem;line-height:1.7;font-weight:300;
    }
    .auth-hero-stats {
      display:flex;gap:2rem;justify-content:center;flex-wrap:wrap;margin-bottom:2rem;
    }
    .auth-stat {display:flex;flex-direction:column;align-items:center;gap:0.2rem;}
    .auth-stat-val {
      font-family:'Bricolage Grotesque',sans-serif;font-size:1.8rem;
      font-weight:700;background:linear-gradient(135deg,#FF6B9D,#A78BFA);
      -webkit-background-clip:text;-webkit-text-fill-color:transparent;
    }
    .auth-stat-lbl {font-size:0.72rem;color:#8888aa;text-transform:uppercase;letter-spacing:0.06em;}
    .auth-feature-pill {
      padding:0.35rem 1rem;border-radius:50px;
      background:rgba(255,255,255,0.9);border:1px solid rgba(255,107,157,0.15);
      font-size:0.78rem;color:#4a4a6a;font-weight:400;
    }

    div.stButton > button {
      border-radius:50px !important;font-family:'DM Sans',sans-serif !important;font-weight:500 !important;
    }
    div.stButton > button[kind="primary"] {
      background:linear-gradient(135deg,#FF6B9D,#A78BFA) !important;
      color:white !important;border:none !important;
      box-shadow:0 4px 20px rgba(255,107,157,0.35) !important;
    }
    .stTextInput input,.stSelectbox>div>div>div,.stNumberInput input {
      border-radius:14px !important;border:1.5px solid rgba(255,107,157,0.15) !important;
      background:rgba(255,255,255,0.9) !important;font-family:'DM Sans',sans-serif !important;
    }
    .stTextInput input:focus {
      border-color:#A78BFA !important;
      box-shadow:0 0 0 3px rgba(167,139,250,0.12) !important;
    }
    .stCheckbox label {font-size:0.85rem !important;color:#4a4a6a !important;}
    .stTabs [data-baseweb="tab-list"] {
      background:rgba(0,0,0,0.04) !important;border-radius:14px !important;padding:4px !important;
    }
    .stTabs [data-baseweb="tab"] {
      border-radius:10px !important;font-family:'DM Sans',sans-serif !important;
    }
    </style>
    """, unsafe_allow_html=True)