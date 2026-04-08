"""
FinPilot AI — Goals & Streak System
"""

import streamlit as st
from datetime import datetime, timedelta
from app.calculators import goal_monthly_saving, sip_future_value
from backend.currency import format_currency

GOAL_CATEGORIES = {
    "emergency":   {"icon":"🛡","color":"#10b981","label":"Emergency Fund"},
    "retirement":  {"icon":"🏖","color":"#A78BFA","label":"Retirement"},
    "purchase":    {"icon":"🏠","color":"#FF6B9D","label":"Big Purchase"},
    "travel":      {"icon":"✈","color":"#06b6d4","label":"Travel"},
    "education":   {"icon":"🎓","color":"#f59e0b","label":"Education"},
    "wedding":     {"icon":"💍","color":"#ec4899","label":"Wedding"},
    "vehicle":     {"icon":"🚗","color":"#8b5cf6","label":"Vehicle"},
    "business":    {"icon":"💼","color":"#FF8C6B","label":"Business"},
    "custom":      {"icon":"⭐","color":"#6366f1","label":"Custom"},
}


def render_goals():
    st.markdown("""
    <div class="fp-fade-in">
    <h2 style="font-family:'Bricolage Grotesque',sans-serif;font-weight:700;
               letter-spacing:-0.03em;margin-bottom:0.25rem;">Goals & Streak System</h2>
    <p style="color:#8888aa;margin-bottom:1.5rem;">
        Set financial goals, track progress, and build winning money habits.
    </p>
    """, unsafe_allow_html=True)

    currency = st.session_state.get("currency","INR")

    # Streak display
    _render_streak_hero()

    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

    col_goals, col_add = st.columns([2, 1])

    with col_goals:
        _render_goals_list(currency)

    with col_add:
        _render_add_goal_form(currency)

    st.markdown("</div>", unsafe_allow_html=True)


def _render_streak_hero():
    streak = st.session_state.get("streak_days", 0)
    state  = st.session_state.get("current_state") or {}
    health = state.get("health_score", 0)

    tier_name  = ("Beginner" if streak < 7 else "Consistent" if streak < 30
                  else "Disciplined" if streak < 90 else "Master")
    tier_color = ("#8888aa" if streak < 7 else "#f59e0b" if streak < 30
                  else "#A78BFA" if streak < 90 else "#FF6B9D")

    cols = st.columns(4)
    items = [
        ("Current Streak",  f"{streak} days",  "🔥",  tier_color),
        ("Best Streak",     f"{max(streak, st.session_state.get('best_streak',streak))} days", "🏆", "#f59e0b"),
        ("Health Score",    f"{health}/100",    "❤",  "#10b981" if health>=70 else "#f59e0b"),
        ("Tier",            tier_name,          "⭐",  tier_color),
    ]

    for col, (label, val, icon, color) in zip(cols, items):
        with col:
            st.markdown(f"""
            <div class="fp-metric" style="border-top:3px solid {color};text-align:center;">
              <div style="font-size:1.5rem;margin-bottom:0.3rem;">{icon}</div>
              <div class="fp-metric-label">{label}</div>
              <div class="fp-metric-value" style="font-size:1.5rem;color:{color};">{val}</div>
            </div>
            """, unsafe_allow_html=True)

    # Streak milestone bar
    milestones = [7, 30, 90, 180, 365]
    next_milestone = next((m for m in milestones if m > streak), 365)
    progress = min(streak / next_milestone, 1.0) * 100

    st.markdown(f"""
    <div class="fp-chart-container" style="margin-top:0.75rem;">
      <div style="display:flex;justify-content:space-between;margin-bottom:0.5rem;">
        <span style="font-size:0.8rem;font-weight:600;">Streak Progress</span>
        <span style="font-size:0.78rem;color:#8888aa;">{streak} / {next_milestone} days to next milestone</span>
      </div>
      <div class="fp-progress">
        <div class="fp-progress-bar" style="width:{progress:.1f}%;background:linear-gradient(90deg,#FF6B9D,#A78BFA);"></div>
      </div>
      <div style="display:flex;justify-content:space-between;margin-top:0.4rem;">
        {''.join(f'<span style="font-size:0.65rem;color:{"#FF6B9D" if streak>=m else "#8888aa"};">{m}d</span>' for m in milestones)}
      </div>
    </div>
    """, unsafe_allow_html=True)


def _render_goals_list(currency: str):
    goals = st.session_state.get("goals", [])

    st.markdown(f"""
    <div class="fp-chart-container">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem;">
        <div class="fp-chart-title" style="margin-bottom:0;">My Financial Goals</div>
        <span style="font-size:0.8rem;color:#8888aa;">{len(goals)} goal{'s' if len(goals)!=1 else ''}</span>
      </div>
    """, unsafe_allow_html=True)

    if not goals:
        st.markdown("""
        <div style="text-align:center;padding:2rem;color:#8888aa;">
          <div style="font-size:2rem;margin-bottom:0.5rem;">🎯</div>
          <div>No goals yet. Add your first financial goal!</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for i, goal in enumerate(goals):
            cat  = goal.get("category","custom")
            meta = GOAL_CATEGORIES.get(cat, GOAL_CATEGORIES["custom"])
            prog = min(100, round(goal.get("current",0) / max(goal.get("target",1),1) * 100, 1))
            bar_color = "#10b981" if prog >= 100 else meta["color"]
            days_left = goal.get("days_left", None)

            st.markdown(f"""
            <div style="padding:1rem;background:var(--bg-secondary,#FFF0F5);
                        border-radius:16px;margin-bottom:0.75rem;
                        border-left:4px solid {meta['color']};">
              <div style="display:flex;justify-content:space-between;align-items:start;margin-bottom:0.6rem;">
                <div style="display:flex;align-items:center;gap:0.5rem;">
                  <span style="font-size:1.2rem;">{meta['icon']}</span>
                  <div>
                    <div style="font-weight:600;font-size:0.9rem;color:var(--text-primary,#1a1a2e);">{goal.get('name','Goal')}</div>
                    <div style="font-size:0.7rem;color:#8888aa;">{meta['label']}</div>
                  </div>
                </div>
                <div style="text-align:right;">
                  <div style="font-weight:700;font-size:0.95rem;color:{meta['color']};">{prog}%</div>
                  {f'<div style="font-size:0.65rem;color:#8888aa;">{days_left} days left</div>' if days_left else ''}
                </div>
              </div>
              <div class="fp-progress">
                <div class="fp-progress-bar" style="width:{prog}%;background:{bar_color};"></div>
              </div>
              <div style="display:flex;justify-content:space-between;margin-top:0.4rem;">
                <span style="font-size:0.75rem;color:#8888aa;">
                  {format_currency(goal.get('current',0),currency,compact=True)} saved
                </span>
                <span style="font-size:0.75rem;color:#8888aa;">
                  Target: {format_currency(goal.get('target',0),currency,compact=True)}
                </span>
              </div>
              {'<div style="display:inline-flex;align-items:center;gap:4px;background:rgba(16,185,129,0.1);color:#10b981;padding:2px 8px;border-radius:6px;font-size:0.65rem;font-weight:700;margin-top:0.4rem;">ACHIEVED</div>' if prog>=100 else ''}
            </div>
            """, unsafe_allow_html=True)

            c1, c2 = st.columns([3,1])
            with c1:
                add_amt = st.number_input(
                    f"Add to {goal.get('name','')}",
                    min_value=0.0, value=0.0, step=1000.0,
                    key=f"goal_add_{i}", label_visibility="collapsed"
                )
            with c2:
                if st.button("Add", key=f"goal_btn_{i}", use_container_width=True):
                    if add_amt > 0:
                        st.session_state.goals[i]["current"] = (
                            goal.get("current",0) + add_amt
                        )
                        if prog + add_amt/max(goal.get("target",1),1)*100 >= 100:
                            st.balloons()
                            st.success(f"Goal '{goal.get('name','')}' achieved!")
                        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def _render_add_goal_form(currency: str):
    st.markdown("""
    <div class="fp-chart-container" style="border-top:3px solid #A78BFA;">
      <div class="fp-chart-title">Add New Goal</div>
    """, unsafe_allow_html=True)

    with st.form("add_goal_form"):
        name = st.text_input("Goal Name", placeholder="e.g. Emergency Fund", key="ag_name")
        cat  = st.selectbox("Category",
                             [f"{v['label']}" for v in GOAL_CATEGORIES.values()],
                             key="ag_cat")
        target = st.number_input(f"Target Amount", min_value=0.0, value=100000.0,
                                  step=10000.0, key="ag_target")
        current = st.number_input("Current Savings", min_value=0.0, value=0.0,
                                   step=1000.0, key="ag_current")
        monthly = st.number_input("Monthly Contribution", min_value=0.0, value=5000.0,
                                   step=500.0, key="ag_monthly")
        ret = st.number_input("Expected Return (%)", 0.0, 30.0, 8.0, 0.5, key="ag_ret")
        deadline = st.date_input("Target Date", value=datetime.now().date() + timedelta(days=365),
                                  key="ag_date")

        submitted = st.form_submit_button("Add Goal", use_container_width=True, type="primary")

    if submitted and name:
        # Map label back to category key
        cat_key = next(
            (k for k, v in GOAL_CATEGORIES.items() if v["label"] == cat), "custom"
        )
        days_left = (deadline - datetime.now().date()).days if deadline else None

        # Calculate monthly needed
        planner = goal_monthly_saving(target, current, ret,
                                       max(1, (days_left or 365)//365))

        new_goal = {
            "name": name,
            "category": cat_key,
            "target": target,
            "current": current,
            "monthly": monthly,
            "return_rate": ret,
            "deadline": str(deadline),
            "days_left": days_left,
            "monthly_needed": planner.get("monthly_saving", monthly),
        }
        if "goals" not in st.session_state:
            st.session_state.goals = []
        st.session_state.goals.append(new_goal)
        st.success(f"Goal '{name}' added!")
        st.rerun()

    # Show projection if state is available
    if st.session_state.get("current_state"):
        st.markdown("<hr style='border:none;border-top:1px solid rgba(0,0,0,0.06);margin:0.75rem 0;'>",
                    unsafe_allow_html=True)
        st.markdown("<div style='font-size:0.78rem;color:#8888aa;'>Monthly savings available based on your current state:</div>",
                    unsafe_allow_html=True)
        surplus = st.session_state.current_state.get("monthly_surplus",0)
        st.markdown(f"<div style='font-weight:700;color:#FF6B9D;font-size:1.1rem;'>{format_currency(surplus, currency)}</div>",
                    unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)