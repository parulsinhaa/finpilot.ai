"""
FinPilot AI — Main Dashboard
KPI cards, charts, AI insights, quick actions, notifications, life events.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import json
from datetime import datetime
from backend.currency import format_currency, convert_state


# ─── Color Palettes per theme ────────────────────────────────────────────────
THEME_COLORS = {
    "pastel":  {"primary":"#FF6B9D","secondary":"#A78BFA","accent":"#FF8C6B",
                "success":"#6EE7B7","bg":"#FFF8F0","card":"#FFFFFF","text":"#1a1a2e"},
    "dark":    {"primary":"#FF6B9D","secondary":"#A78BFA","accent":"#FF8C6B",
                "success":"#10b981","bg":"#0d0d1a","card":"#1a1a2e","text":"#f0f0ff"},
    "minimal": {"primary":"#e11d48","secondary":"#7c3aed","accent":"#f59e0b",
                "success":"#10b981","bg":"#ffffff","card":"#f8f9fa","text":"#111827"},
    "ocean":   {"primary":"#06b6d4","secondary":"#6366f1","accent":"#0ea5e9",
                "success":"#10b981","bg":"#0a1628","card":"#0d1f3c","text":"#e0f2fe"},
}


def get_colors():
    return THEME_COLORS.get(st.session_state.get("theme","pastel"), THEME_COLORS["pastel"])


def render_dashboard():
    st.markdown("<div class='fp-fade-in'>", unsafe_allow_html=True)

    env  = st.session_state.get("env")
    state = st.session_state.get("current_state") or {}
    history = st.session_state.get("history", [])
    currency = st.session_state.get("currency", "INR")
    C = get_colors()

    # Convert state to display currency if needed
    if state.get("currency","INR") != currency:
        display_state = convert_state(state, currency)
    else:
        display_state = state

    # ── Top Bar ──────────────────────────────────────────────────────────────
    col_title, col_actions = st.columns([3, 1])
    with col_title:
        user = st.session_state.get("user") or {}
        hour = datetime.now().hour
        greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 17 else "Good evening"
        name = user.get("name", "User").split()[0]
        month = state.get("month", 0)
        life_event = state.get("life_event", "none")

        st.markdown(f"""
        <div style="margin-bottom:0.25rem;">
          <span style="color:var(--text-muted,#8888aa);font-size:0.85rem;">{greeting},</span>
          <span style="font-family:'Bricolage Grotesque',sans-serif;font-size:1.6rem;
                       font-weight:700;color:{C['text']};margin-left:0.4rem;
                       letter-spacing:-0.02em;">{name}</span>
          <span style="font-size:0.8rem;color:var(--text-muted,#8888aa);margin-left:0.5rem;">
            — Month {month}
          </span>
        </div>
        """, unsafe_allow_html=True)

        # Life event badge
        if life_event != "none":
            event_map = {
                "salary_increase":  ("positive","Salary Increase"),
                "promotion":        ("positive","Promotion"),
                "windfall":         ("positive","Windfall Received"),
                "medical_emergency":("negative","Medical Emergency"),
                "job_loss":         ("negative","Job Loss"),
                "market_crash":     ("negative","Market Crash"),
                "expense_spike":    ("negative","Expense Spike"),
            }
            ev_type, ev_label = event_map.get(life_event, ("neutral", life_event.replace("_"," ").title()))
            impact = display_state.get("life_event_impact", 0)
            sign = "+" if impact >= 0 else ""
            st.markdown(f"""
            <div class="fp-event-badge {ev_type}" style="margin-top:0.4rem;display:inline-flex;">
              <span>{"⬆" if ev_type=="positive" else "⚠"}</span>
              <span>{ev_label} &nbsp;|&nbsp; {sign}{format_currency(abs(impact),currency,compact=True)}</span>
            </div>
            """, unsafe_allow_html=True)

    with col_actions:
        if st.button("Next Month  ▶", use_container_width=True, type="primary"):
            _advance_month(env)

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    # ── KPI Cards Row ─────────────────────────────────────────────────────────
    _render_kpi_row(display_state, currency, C)

    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

    # ── Main Content ──────────────────────────────────────────────────────────
    col_left, col_right = st.columns([2, 1])

    with col_left:
        _render_net_worth_chart(history, currency, C)
        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
        _render_expense_chart(display_state, C)

    with col_right:
        _render_ai_insights_panel(state, C)
        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
        _render_notifications_panel()

    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

    # ── Quick Actions ─────────────────────────────────────────────────────────
    _render_quick_actions(env, display_state, currency)

    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

    # ── Goals Progress + Simulation Log ──────────────────────────────────────
    col_g, col_l = st.columns([1, 1])
    with col_g:
        _render_goals_mini(currency)
    with col_l:
        _render_sim_log(history, currency)

    st.markdown("</div>", unsafe_allow_html=True)


# ─── KPI Row ─────────────────────────────────────────────────────────────────

def _render_kpi_row(state, currency, C):
    cols = st.columns(4)

    kpis = [
        ("Net Worth",      state.get("net_worth",0),      "net_worth_change_pct",  C["secondary"]),
        ("Total Savings",  state.get("savings",0),         "savings_rate",          C["primary"]),
        ("Investments",    state.get("investments",0),     None,                    C["success"]),
        ("Total Debt",     state.get("debt",0),            None,                    C["accent"]),
    ]

    for col, (label, value, delta_key, color) in zip(cols, kpis):
        with col:
            fv = format_currency(value, currency, compact=True)
            delta_html = ""
            if delta_key:
                delta = state.get(delta_key, 0)
                if delta_key == "savings_rate":
                    delta_html = f'<div class="fp-metric-delta positive">{delta*100:.1f}% savings rate</div>'
                elif delta > 0:
                    delta_html = f'<div class="fp-metric-delta positive">▲ {delta*100:.1f}%</div>'
                elif delta < 0:
                    delta_html = f'<div class="fp-metric-delta negative">▼ {abs(delta)*100:.1f}%</div>'

            negative_color = "#ef4444" if label == "Total Debt" else C["text"] if True else ""
            val_color = "#ef4444" if (label == "Total Debt" and value > 0) else C["text"]

            st.markdown(f"""
            <div class="fp-metric" style="border-top:3px solid {color};">
              <div class="fp-metric-label">{label}</div>
              <div class="fp-metric-value" style="color:{val_color};">{fv}</div>
              {delta_html}
            </div>
            """, unsafe_allow_html=True)


# ─── Net Worth Chart ─────────────────────────────────────────────────────────

def _render_net_worth_chart(history, currency, C):
    st.markdown(f"""
    <div class="fp-chart-container">
      <div class="fp-chart-title">Net Worth Trajectory</div>
    """, unsafe_allow_html=True)

    if len(history) >= 2:
        months = [h.get("month", i+1) for i, h in enumerate(history)]
        nw     = [h.get("net_worth", 0) for h in history]
        sav    = [h.get("savings", 0) for h in history]
        inv    = [h.get("investments", 0) for h in history]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=months, y=nw, name="Net Worth",
            fill="tozeroy",
            fillcolor=f"rgba(167,139,250,0.15)",
            line=dict(color=C["secondary"], width=2.5),
            mode="lines",
        ))
        fig.add_trace(go.Scatter(
            x=months, y=sav, name="Savings",
            line=dict(color=C["primary"], width=2, dash="dot"),
            mode="lines",
        ))
        fig.add_trace(go.Scatter(
            x=months, y=inv, name="Investments",
            line=dict(color=C["success"], width=2, dash="dash"),
            mode="lines",
        ))

        fig.update_layout(
            height=240,
            margin=dict(l=0, r=0, t=10, b=0),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="right", x=1,
                        font=dict(size=11)),
            xaxis=dict(showgrid=False, tickfont=dict(size=10), title="Month"),
            yaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.05)",
                       tickfont=dict(size=10),
                       tickformat=","),
            font=dict(family="DM Sans, sans-serif"),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("Run a few months to see your net worth trajectory chart.")

    st.markdown("</div>", unsafe_allow_html=True)


# ─── Expense Breakdown Chart ─────────────────────────────────────────────────

def _render_expense_chart(state, C):
    st.markdown("""
    <div class="fp-chart-container">
      <div class="fp-chart-title">Monthly Expense Breakdown</div>
    """, unsafe_allow_html=True)

    expenses = state.get("expenses", {})
    if expenses:
        labels = [k.replace("_"," ").title() for k in expenses.keys()]
        values = list(expenses.values())
        colors = [C["primary"], C["secondary"], C["accent"], C["success"],
                  "#f59e0b","#3b82f6","#ec4899","#8b5cf6","#06b6d4","#84cc16"]

        fig = go.Figure(go.Bar(
            x=labels, y=values,
            marker_color=colors[:len(labels)],
            marker_line_width=0,
            text=[f"{v:,.0f}" for v in values],
            textposition="outside",
            textfont=dict(size=10),
        ))
        fig.update_layout(
            height=220,
            margin=dict(l=0, r=0, t=10, b=0),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(tickfont=dict(size=9), showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.05)",
                       tickfont=dict(size=10)),
            font=dict(family="DM Sans, sans-serif"),
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown("</div>", unsafe_allow_html=True)


# ─── AI Insights Panel ───────────────────────────────────────────────────────

def _render_ai_insights_panel(state, C):
    env = st.session_state.get("env")
    st.markdown(f"""
    <div class="fp-chart-container" style="border-top:3px solid {C['primary']};">
      <div class="fp-chart-title">AI Advisor Insights</div>
    """, unsafe_allow_html=True)

    insights = st.session_state.get("last_insights", [])
    if not insights and env:
        try:
            insights = env.ai_engine.generate_insights(state, [])
            st.session_state.last_insights = insights
        except Exception:
            insights = []

    if insights:
        type_styles = {
            "positive": ("positive", "▲"),
            "warning":  ("warning",  "▲"),
            "neutral":  ("info",     "●"),
            "action":   ("ai",       "→"),
        }
        for ins in insights[:4]:
            t = ins.get("type", "neutral")
            cls, icon = type_styles.get(t, ("info","●"))
            st.markdown(f"""
            <div class="fp-notification {cls}">
              <div>
                <div style="font-weight:600;font-size:0.85rem;color:var(--text-primary,#1a1a2e);">
                  {icon} {ins.get('title','')}
                </div>
                <div style="font-size:0.78rem;color:var(--text-muted,#8888aa);margin-top:2px;line-height:1.5;">
                  {ins.get('detail','')}
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        # Fallback rule-based insight
        hs = state.get("health_score", 0)
        sr = state.get("savings_rate", 0)
        st.markdown(f"""
        <div class="fp-notification ai">
          <div>
            <div style="font-weight:600;font-size:0.85rem;">AI Analysis</div>
            <div style="font-size:0.78rem;color:#8888aa;margin-top:2px;">
              Health Score: {hs}/100 · Savings Rate: {sr*100:.1f}%<br>
              {'Excellent financial health. Keep investing!' if hs>=70 else
               'Focus on building emergency fund and reducing debt.' if hs<50 else
               'Good progress. Increase savings rate toward 20%.'}
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    if st.button("Chat with AI Advisor", use_container_width=True):
        st.session_state.current_page = "ai_chat"
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# ─── Notifications Panel ─────────────────────────────────────────────────────

def _render_notifications_panel():
    notifications = st.session_state.get("notifications", [])
    unread = [n for n in notifications if not n.get("read", False)]

    st.markdown(f"""
    <div class="fp-chart-container">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.75rem;">
        <div class="fp-chart-title" style="margin-bottom:0;">Notifications</div>
        {'<span style="background:linear-gradient(135deg,#FF6B9D,#A78BFA);color:white;font-size:0.65rem;font-weight:700;padding:2px 8px;border-radius:50px;">' + str(len(unread)) + ' new</span>' if unread else ''}
      </div>
    """, unsafe_allow_html=True)

    if notifications:
        for n in notifications[-5:][::-1]:
            t = n.get("type", "info")
            cls_map = {"ai":"ai","alert":"negative","achievement":"positive",
                       "warning":"warning","report":"info","reminder":"neutral","info":"info"}
            cls = cls_map.get(t,"info")
            read_style = "opacity:0.6;" if n.get("read") else ""
            st.markdown(f"""
            <div class="fp-notification {cls}" style="{read_style}cursor:pointer;"
                 onclick="this.style.opacity='0.5'">
              <div>
                <div style="font-weight:600;font-size:0.82rem;color:var(--text-primary,#1a1a2e);">
                  {n.get('title','')}
                </div>
                <div style="font-size:0.73rem;color:var(--text-muted,#8888aa);margin-top:1px;line-height:1.4;">
                  {n.get('body','')[:80]}{'...' if len(n.get('body',''))>80 else ''}
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

        if st.button("Mark all as read", use_container_width=True):
            for n in st.session_state.notifications:
                n["read"] = True
            st.session_state.unread_count = 0
            st.rerun()
    else:
        st.markdown("<p style='color:#8888aa;font-size:0.85rem;'>No notifications yet.</p>",
                    unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# ─── Quick Actions ───────────────────────────────────────────────────────────

def _render_quick_actions(env, state, currency):
    st.markdown("""
    <div class="fp-chart-container">
      <div class="fp-chart-title">Quick Actions</div>
    """, unsafe_allow_html=True)

    surplus = state.get("monthly_surplus", 0)
    income  = state.get("income", 1)

    cols = st.columns(5)
    actions = [
        ("Invest SIP",    "invest_sip",          {"amount": round(surplus*0.3,2), "fund_type":"equity_index"}),
        ("Save",          "save",                {"amount": round(surplus*0.4,2)}),
        ("Repay Debt",    "repay_debt",           {"amount": round(surplus*0.3,2)}),
        ("Emerg. Fund",   "build_emergency_fund", {"amount": round(surplus*0.25,2)}),
        ("AI Decide",     "ai",                  {}),
    ]

    for col, (label, action_type, params) in zip(cols, actions):
        with col:
            if st.button(label, use_container_width=True, key=f"qa_{action_type}"):
                if action_type == "ai":
                    _ai_step(env)
                else:
                    _manual_step(env, action_type, params)

    st.markdown("</div>", unsafe_allow_html=True)


# ─── Goals Mini ──────────────────────────────────────────────────────────────

def _render_goals_mini(currency):
    goals = st.session_state.get("goals", [])
    C = get_colors()

    st.markdown(f"""
    <div class="fp-chart-container">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.75rem;">
        <div class="fp-chart-title" style="margin-bottom:0;">Financial Goals</div>
      </div>
    """, unsafe_allow_html=True)

    if goals:
        for g in goals[:4]:
            prog = min(100, round(g.get("current",0) / max(g.get("target",1), 1) * 100))
            bar_color = C["success"] if prog >= 100 else C["primary"]
            st.markdown(f"""
            <div style="margin-bottom:0.8rem;">
              <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
                <span style="font-size:0.82rem;font-weight:500;color:var(--text-primary,#1a1a2e);">{g.get('name','Goal')}</span>
                <span style="font-size:0.78rem;color:var(--text-muted,#8888aa);">{prog}%</span>
              </div>
              <div class="fp-progress">
                <div class="fp-progress-bar" style="width:{prog}%;background:{bar_color};"></div>
              </div>
              <div style="font-size:0.72rem;color:var(--text-muted,#8888aa);margin-top:2px;">
                {format_currency(g.get('current',0),currency,compact=True)} /
                {format_currency(g.get('target',0),currency,compact=True)}
              </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("<p style='color:#8888aa;font-size:0.85rem;'>No goals set yet.</p>",
                    unsafe_allow_html=True)
        if st.button("Add First Goal", use_container_width=True):
            st.session_state.current_page = "goals"
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# ─── Simulation Log ──────────────────────────────────────────────────────────

def _render_sim_log(history, currency):
    st.markdown("""
    <div class="fp-chart-container">
      <div class="fp-chart-title">Simulation Log</div>
      <div style="max-height:220px;overflow-y:auto;scrollbar-width:thin;">
    """, unsafe_allow_html=True)

    if history:
        for h in reversed(history[-8:]):
            month = h.get("month", "?")
            event = h.get("life_event","none")
            nw    = format_currency(h.get("net_worth",0), currency, compact=True)
            hs    = h.get("health_score",0)
            color = "#10b981" if event == "none" else "#f59e0b" if "increase" in event or event in ["windfall","promotion"] else "#ef4444"
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;align-items:center;
                        padding:0.4rem 0;border-bottom:1px solid rgba(0,0,0,0.04);">
              <div>
                <span style="font-size:0.75rem;font-weight:600;color:var(--text-primary,#1a1a2e);">
                  Month {month}</span>
                {f'<span style="font-size:0.65rem;background:rgba(239,68,68,0.1);color:{color};padding:1px 6px;border-radius:6px;margin-left:6px;">{event.replace("_"," ")}</span>' if event!="none" else ''}
              </div>
              <div style="text-align:right;">
                <div style="font-size:0.78rem;font-weight:600;color:var(--text-primary,#1a1a2e);">{nw}</div>
                <div style="font-size:0.65rem;color:#8888aa;">Score: {hs}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("<p style='color:#8888aa;font-size:0.85rem;'>Press 'Next Month' to start simulation.</p>",
                    unsafe_allow_html=True)

    st.markdown("</div></div>", unsafe_allow_html=True)


# ─── Actions ─────────────────────────────────────────────────────────────────

def _advance_month(env):
    if env is None:
        st.error("Environment not initialised.")
        return
    try:
        action, reasoning = env.ai_decide()
        result = env.step(action)
        _update_session(result, action, reasoning)
    except Exception as e:
        st.error(f"Simulation error: {e}")


def _ai_step(env):
    if env is None: return
    try:
        action, reasoning = env.ai_decide()
        result = env.step(action)
        _update_session(result, action, reasoning)
    except Exception as e:
        st.error(f"AI step error: {e}")


def _manual_step(env, action_type, params):
    if env is None: return
    try:
        action = {"type": action_type, "params": params}
        result = env.step(action)
        _update_session(result, action, f"Manual action: {action_type}")
    except Exception as e:
        st.error(f"Action error: {e}")


def _update_session(result, action, reasoning):
    new_state = result["state"]
    st.session_state.current_state = new_state
    st.session_state.history.append({**new_state, "action": action, "reasoning": reasoning})
    st.session_state.streak_days = new_state.get("streak_days", 0)
    st.session_state.last_insights = []  # Clear to refresh

    # Add notification for life event
    event = new_state.get("life_event","none")
    if event != "none":
        event_labels = {
            "salary_increase":"Salary Increase!", "medical_emergency":"Medical Emergency",
            "job_loss":"Job Loss Event","market_crash":"Market Crash",
            "windfall":"Windfall Received!","promotion":"Promotion!",
        }
        body_map = {
            "salary_increase": f"Your income increased this month.",
            "medical_emergency":"An emergency expense hit your fund. Check your balance.",
            "job_loss":"Employment disrupted. AI is rebalancing your plan.",
            "market_crash":"Portfolio took a hit. Stay the course.",
            "windfall":"Extra money received. AI is optimising allocation.",
            "promotion":"Income boost! Great time to increase investments.",
        }
        notif = {
            "title": event_labels.get(event, event.replace("_"," ").title()),
            "body":  body_map.get(event, "A financial event occurred this month."),
            "type":  "positive" if event in ["salary_increase","windfall","promotion"] else "warning",
            "read":  False,
        }
        st.session_state.notifications.append(notif)
        unread = sum(1 for n in st.session_state.notifications if not n.get("read"))
        st.session_state.unread_count = unread

    st.rerun()