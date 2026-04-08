"""
FinPilot AI — What-If Simulation Engine
Compare multiple financial strategies side-by-side.
"""

import streamlit as st
import plotly.graph_objects as go
from backend.currency import format_currency


STRATEGIES = {
    "Aggressive Investing":  {"type":"invest_sip",          "params":{"amount":25000,"fund_type":"equity"}},
    "Aggressive Debt Payoff":{"type":"repay_debt",           "params":{"amount":20000}},
    "Balanced (Save+Invest)":{"type":"save",                 "params":{"amount":15000}},
    "Emergency Fund First":  {"type":"build_emergency_fund", "params":{"amount":18000}},
    "AI Recommended":        {"type":"ai",                   "params":{}},
}


def render_what_if():
    st.markdown("""
    <div class="fp-fade-in">
    <h2 style="font-family:'Bricolage Grotesque',sans-serif;font-weight:700;
               letter-spacing:-0.03em;margin-bottom:0.25rem;">What-If Simulation</h2>
    <p style="color:#8888aa;margin-bottom:1.5rem;">
        Test financial decisions before making them. Compare strategies over time.
    </p>
    """, unsafe_allow_html=True)

    env      = st.session_state.get("env")
    state    = st.session_state.get("current_state") or {}
    currency = st.session_state.get("currency","INR")

    if env is None:
        st.warning("Please sign in and start a simulation first.")
        return

    col_config, col_results = st.columns([1, 2])

    # ── Configuration ─────────────────────────────────────────────────────────
    with col_config:
        st.markdown("""
        <div class="fp-chart-container" style="border-top:3px solid #A78BFA;">
          <div class="fp-chart-title">Scenario Builder</div>
        """, unsafe_allow_html=True)

        months = st.slider("Projection Horizon (months)", 3, 36, 12, key="wi_months")

        st.markdown("<div style='font-size:0.78rem;font-weight:600;color:#8888aa;text-transform:uppercase;letter-spacing:0.06em;margin:0.75rem 0 0.4rem;'>Select Strategies to Compare</div>",
                    unsafe_allow_html=True)

        selected = []
        for label in STRATEGIES:
            if st.checkbox(label, value=(label in ["Aggressive Investing","Balanced (Save+Invest)"]),
                           key=f"wi_{label}"):
                selected.append(label)

        st.markdown("<hr style='border:none;border-top:1px solid rgba(0,0,0,0.06);margin:0.75rem 0;'>",
                    unsafe_allow_html=True)

        # Custom scenario
        st.markdown("<div style='font-size:0.85rem;font-weight:600;color:var(--text-primary,#1a1a2e);margin-bottom:0.5rem;'>Custom Scenario</div>",
                    unsafe_allow_html=True)
        custom_type = st.selectbox("Action Type",
                                    ["save","invest_sip","repay_debt",
                                     "build_emergency_fund","adjust_expenses"],
                                    key="wi_custom_type")
        custom_amount = st.number_input(f"Amount ({currency})", 0.0, value=10000.0, step=1000.0,
                                         key="wi_custom_amount")
        custom_name = st.text_input("Label", value="My Strategy", key="wi_custom_name")

        if st.button("Add Custom Strategy"):
            selected.append(f"__custom__{custom_name}")
            STRATEGIES[f"__custom__{custom_name}"] = {
                "type": custom_type,
                "params": {"amount": custom_amount}
            }

        if st.button("Run Simulation", type="primary", use_container_width=True):
            if selected:
                _run_comparison(env, selected, months, currency)
            else:
                st.warning("Select at least one strategy.")

        st.markdown("</div>", unsafe_allow_html=True)

        # Macro scenario overrides
        st.markdown("""
        <div class="fp-chart-container" style="margin-top:0.75rem;">
          <div class="fp-chart-title">Macro Scenarios</div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='font-size:0.78rem;color:#8888aa;margin-bottom:0.5rem;'>Apply a macro event to all scenarios:</div>",
                    unsafe_allow_html=True)

        macro = st.radio("",
                          ["Normal","Salary +20%","Salary -30%","Market Crash","Inflation +4%"],
                          key="wi_macro", label_visibility="collapsed")

        macro_overrides = {
            "Normal":        {},
            "Salary +20%":   {"income": state.get("income",0)*1.20},
            "Salary -30%":   {"income": state.get("income",0)*0.70},
            "Market Crash":  {"investments": state.get("investments",0)*0.65,
                              "market_sentiment":"bearish"},
            "Inflation +4%": {"inflation_rate": state.get("inflation_rate",6)+4},
        }
        st.session_state.wi_macro_overrides = macro_overrides.get(macro, {})

        st.markdown("</div>", unsafe_allow_html=True)

    # ── Results ───────────────────────────────────────────────────────────────
    with col_results:
        if "wi_results" in st.session_state and st.session_state.wi_results:
            _render_results(st.session_state.wi_results, currency)
        else:
            st.markdown("""
            <div class="fp-chart-container" style="text-align:center;padding:3rem;">
              <div style="font-size:2.5rem;margin-bottom:1rem;">🔮</div>
              <div style="font-size:1.1rem;font-weight:600;color:var(--text-primary,#1a1a2e);margin-bottom:0.5rem;">
                Run a simulation to see results
              </div>
              <div style="color:#8888aa;font-size:0.88rem;">
                Select strategies on the left and click Run Simulation
              </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def _run_comparison(env, selected_labels, months, currency):
    results = {}
    overrides = st.session_state.get("wi_macro_overrides", {})

    with st.spinner("Simulating all strategies..."):
        for label in selected_labels:
            strategy = STRATEGIES.get(label, {})
            if strategy.get("type") == "ai":
                try:
                    action, _ = env.ai_decide()
                except Exception:
                    action = {"type":"save","params":{"amount":10000}}
            else:
                action = {"type": strategy["type"], "params": strategy["params"]}

            scenario = {
                "action": action,
                "months": months,
                "state_overrides": overrides,
            }

            try:
                projections = env.what_if(scenario)
                display_label = label.replace("__custom__","")
                results[display_label] = projections
            except Exception as e:
                st.error(f"Error simulating '{label}': {e}")

    if results:
        st.session_state.wi_results = results
        st.rerun()


def _render_results(results, currency):
    COLORS = ["#A78BFA","#FF6B9D","#10b981","#f59e0b","#06b6d4","#ec4899"]

    # Net worth comparison chart
    st.markdown("""
    <div class="fp-chart-container" style="border-top:3px solid #FF6B9D;">
      <div class="fp-chart-title">Net Worth Projection — Strategy Comparison</div>
    """, unsafe_allow_html=True)

    fig = go.Figure()
    for i, (label, projections) in enumerate(results.items()):
        months = [p["month"] for p in projections]
        nw     = [p["net_worth"] for p in projections]
        color  = COLORS[i % len(COLORS)]
        fig.add_trace(go.Scatter(
            x=months, y=nw, name=label,
            line=dict(color=color, width=2.5),
            mode="lines+markers",
            marker=dict(size=4),
        ))

    fig.update_layout(
        height=300,
        margin=dict(l=0,r=0,t=10,b=0),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", y=-0.15),
        xaxis_title="Month",
        yaxis_title=f"Net Worth ({currency})",
        font=dict(family="DM Sans,sans-serif",size=11),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True,gridcolor="rgba(0,0,0,0.05)"),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
    st.markdown("</div>", unsafe_allow_html=True)

    # Summary table
    st.markdown("""
    <div class="fp-chart-container" style="margin-top:0.75rem;">
      <div class="fp-chart-title">Strategy Summary</div>
      <table class="fp-table">
        <thead>
          <tr>
            <th>Strategy</th>
            <th>Final Net Worth</th>
            <th>Final Savings</th>
            <th>Final Debt</th>
            <th>Health Score</th>
          </tr>
        </thead>
        <tbody>
    """, unsafe_allow_html=True)

    best_nw = max((p[-1]["net_worth"] for p in results.values() if p), default=0)

    for i, (label, projections) in enumerate(results.items()):
        if not projections: continue
        final = projections[-1]
        color = COLORS[i % len(COLORS)]
        nw    = final.get("net_worth", 0)
        bold  = "font-weight:700;" if nw == best_nw else ""
        check = " ✓" if nw == best_nw else ""

        st.markdown(f"""
        <tr>
          <td><span style="color:{color};font-weight:600;">{label}{check}</span></td>
          <td style="{bold}">{format_currency(nw, currency, compact=True)}</td>
          <td>{format_currency(final.get('savings',0), currency, compact=True)}</td>
          <td>{format_currency(final.get('debt',0), currency, compact=True)}</td>
          <td><span style="color:{'#10b981' if final.get('health_score',0)>=70 else '#f59e0b'};">
            {final.get('health_score',0)}/100</span></td>
        </tr>
        """, unsafe_allow_html=True)

    st.markdown("</tbody></table></div>", unsafe_allow_html=True)

    # Best strategy callout
    best_label = max(results, key=lambda k: results[k][-1]["net_worth"] if results[k] else 0)
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,rgba(167,139,250,0.1),rgba(255,107,157,0.1));
                border:1px solid rgba(167,139,250,0.25);border-radius:16px;
                padding:1rem 1.25rem;margin-top:0.75rem;display:flex;align-items:center;gap:0.75rem;">
      <span style="font-size:1.5rem;">🏆</span>
      <div>
        <div style="font-weight:700;font-size:0.9rem;">Best Strategy for Your Situation</div>
        <div style="color:#8888aa;font-size:0.82rem;">
          <strong style="color:#A78BFA;">{best_label}</strong> produces the highest net worth
          across your {len(list(results.values())[0]) if results else 0}-month projection.
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)