"""
FinPilot AI — AI Chat Assistant
Full conversational AI advisor with financial context.
"""

import streamlit as st
import time


QUICK_PROMPTS = [
    "How can I improve my health score?",
    "Should I pay off debt or invest?",
    "How much emergency fund do I need?",
    "What SIP amount should I start with?",
    "Explain my net worth breakdown",
    "How can I reach financial freedom faster?",
    "What is the best strategy for my debt?",
    "How will inflation affect my savings?",
]


def render_ai_chat():
    st.markdown("""
    <div class="fp-fade-in">
    <h2 style="font-family:'Bricolage Grotesque',sans-serif;font-weight:700;
               letter-spacing:-0.03em;margin-bottom:0.25rem;">AI Financial Advisor</h2>
    <p style="color:#8888aa;margin-bottom:1.5rem;">
        Ask anything about your finances. Your AI advisor knows your complete financial state.
    </p>
    """, unsafe_allow_html=True)

    env   = st.session_state.get("env")
    state = st.session_state.get("current_state") or {}

    col_chat, col_context = st.columns([2, 1])

    # ── Chat Panel ────────────────────────────────────────────────────────────
    with col_chat:
        st.markdown("""
        <div class="fp-chart-container" style="border-top:3px solid #FF6B9D;">
          <div class="fp-chart-title">Chat with FinPilot AI</div>
        """, unsafe_allow_html=True)

        # Quick prompts
        st.markdown("<div style='margin-bottom:0.75rem;'>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:0.75rem;color:#8888aa;margin-bottom:0.4rem;font-weight:500;text-transform:uppercase;letter-spacing:0.06em;'>Quick Questions</div>",
                    unsafe_allow_html=True)

        cols = st.columns(4)
        for i, prompt in enumerate(QUICK_PROMPTS[:4]):
            with cols[i % 4]:
                if st.button(prompt[:28] + "..." if len(prompt) > 28 else prompt,
                             key=f"qp_{i}", use_container_width=True):
                    _send_message(prompt, env, state)

        cols2 = st.columns(4)
        for i, prompt in enumerate(QUICK_PROMPTS[4:]):
            with cols2[i % 4]:
                if st.button(prompt[:28] + "..." if len(prompt) > 28 else prompt,
                             key=f"qp2_{i}", use_container_width=True):
                    _send_message(prompt, env, state)

        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<hr style='border:none;border-top:1px solid rgba(255,107,157,0.1);margin:0.75rem 0;'>",
                    unsafe_allow_html=True)

        # Messages
        messages = st.session_state.get("chat_messages", [])
        if not messages:
            st.markdown("""
            <div style="text-align:center;padding:2rem;color:#8888aa;">
              <div style="font-size:2rem;margin-bottom:0.5rem;">🤖</div>
              <div style="font-size:0.9rem;font-weight:500;">Ask me anything about your finances</div>
              <div style="font-size:0.8rem;margin-top:0.3rem;">
                I have full access to your financial state and simulation history.
              </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            chat_container = st.container()
            with chat_container:
                for msg in messages:
                    _render_message(msg)

        st.markdown("</div>", unsafe_allow_html=True)

        # Input area
        col_input, col_lang, col_send = st.columns([5, 1.5, 1])
        with col_input:
            user_input = st.text_input(
                "Message",
                placeholder="Ask about your savings, investments, debt, goals...",
                key="chat_input",
                label_visibility="collapsed",
            )
        with col_lang:
            lang = st.selectbox(
                "Language",
                ["English","Hindi","Spanish","French"],
                index=["English","Hindi","Spanish","French"].index(
                    st.session_state.get("language","English")
                ),
                key="chat_lang",
                label_visibility="collapsed",
            )
        with col_send:
            if st.button("Send", type="primary", use_container_width=True):
                if user_input.strip():
                    if env:
                        env.ai_engine.language = lang
                    _send_message(user_input.strip(), env, state)

        if st.button("Clear Chat History"):
            st.session_state.chat_messages = []
            if env:
                env.ai_engine.conversation_history = []
            st.rerun()

    # ── Context Panel ─────────────────────────────────────────────────────────
    with col_context:
        st.markdown("""
        <div class="fp-chart-container" style="border-top:3px solid #A78BFA;">
          <div class="fp-chart-title">Your Financial Snapshot</div>
        """, unsafe_allow_html=True)

        currency = st.session_state.get("currency","INR")
        metrics = [
            ("Net Worth",      state.get("net_worth",0),     currency),
            ("Health Score",   state.get("health_score",0),  None),
            ("Savings",        state.get("savings",0),       currency),
            ("Investments",    state.get("investments",0),   currency),
            ("Debt",           state.get("debt",0),          currency),
            ("Savings Rate",   state.get("savings_rate",0),  "pct"),
            ("Emergency Fund", state.get("emergency_fund",0),currency),
            ("Month",          state.get("month",0),         None),
        ]

        for label, value, unit in metrics:
            if unit == "pct":
                formatted = f"{value*100:.1f}%"
            elif unit:
                formatted = format_currency(value, unit, compact=True) if hasattr(value, '__float__') else str(value)
            else:
                formatted = str(value)

            color = "#10b981" if (label=="Health Score" and value>=70) else \
                    "#ef4444"  if (label=="Total Debt"  and value>0)   else \
                    "var(--text-primary,#1a1a2e)"

            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;padding:0.4rem 0;
                        border-bottom:1px solid rgba(0,0,0,0.04);">
              <span style="font-size:0.78rem;color:#8888aa;">{label}</span>
              <span style="font-size:0.82rem;font-weight:600;color:{color};">{formatted}</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

        # Life event context
        event = state.get("life_event","none")
        if event != "none":
            st.markdown(f"""
            <div class="fp-notification warning">
              <div>
                <div style="font-weight:600;font-size:0.82rem;">Active Life Event</div>
                <div style="font-size:0.75rem;color:#8888aa;">{event.replace('_',' ').title()}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

        # AI status
        has_api = bool(st.session_state.get("env") and
                        __import__("os").environ.get("OPENAI_API_KEY",""))
        status_color = "#10b981" if has_api else "#f59e0b"
        status_text  = "GPT-4o Connected" if has_api else "Rule Engine (Add API Key)"
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:0.5rem;padding:0.6rem;
                    background:rgba(0,0,0,0.03);border-radius:10px;margin-top:0.5rem;">
          <div style="width:8px;height:8px;border-radius:50%;background:{status_color};"></div>
          <span style="font-size:0.75rem;color:#8888aa;">{status_text}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def _send_message(text: str, env, state: dict):
    """Send message and get AI response."""
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    # Add user message
    st.session_state.chat_messages.append({"role":"user","content":text})

    # Get AI response
    if env:
        with st.spinner("FinPilot AI is thinking..."):
            try:
                response = env.ai_chat(text)
            except Exception as e:
                response = f"I encountered an issue: {e}. Please try again."
    else:
        response = "Environment not initialised. Please sign in first."

    st.session_state.chat_messages.append({"role":"ai","content":response})
    # Clear input
    if "chat_input" in st.session_state:
        st.session_state.chat_input = ""
    st.rerun()


def _render_message(msg: dict):
    role = msg.get("role","user")
    content = msg.get("content","")

    if role == "user":
        st.markdown(f"""
        <div class="fp-chat-message user">
          <div class="fp-chat-bubble">{content}</div>
          <div class="fp-chat-avatar user">U</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="fp-chat-message ai">
          <div class="fp-chat-avatar ai">AI</div>
          <div class="fp-chat-bubble">{content}</div>
        </div>
        """, unsafe_allow_html=True)


def format_currency(amount, currency="INR", compact=False):
    try:
        from backend.currency import format_currency as fc
        return fc(amount, currency, compact)
    except Exception:
        return f"{amount:,.0f} {currency}"