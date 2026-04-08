"""
FinPilot AI — Monthly Report Generator
"""

import streamlit as st
from datetime import datetime
from backend.currency import format_currency
import plotly.graph_objects as go


def render_reports():
    st.markdown("""
    <div class="fp-fade-in">
    <h2 style="font-family:'Bricolage Grotesque',sans-serif;font-weight:700;
               letter-spacing:-0.03em;margin-bottom:0.25rem;">Financial Reports</h2>
    <p style="color:#8888aa;margin-bottom:1.5rem;">
        AI-generated monthly financial analysis and strategy reports.
    </p>
    """, unsafe_allow_html=True)

    env      = st.session_state.get("env")
    state    = st.session_state.get("current_state") or {}
    history  = st.session_state.get("history", [])
    currency = st.session_state.get("currency","INR")

    col_meta, col_content = st.columns([1, 2])

    with col_meta:
        st.markdown("""
        <div class="fp-chart-container" style="border-top:3px solid #FF6B9D;">
          <div class="fp-chart-title">Generate Report</div>
        """, unsafe_allow_html=True)

        month    = state.get("month", 0)
        language = st.session_state.get("language","English")
        report_type = st.selectbox("Report Type",
                                    ["Monthly Summary","Investment Analysis",
                                     "Debt Strategy Report","Full Financial Review"],
                                    key="report_type")
        lang = st.selectbox("Language", ["English","Hindi","Spanish","French"],
                             index=["English","Hindi","Spanish","French"].index(language),
                             key="report_lang")

        if st.button("Generate AI Report", type="primary", use_container_width=True):
            if env and month > 0:
                with st.spinner("AI is writing your report..."):
                    try:
                        env.ai_engine.language = lang
                        report = env.monthly_report()
                        st.session_state.current_report = report
                        st.session_state.report_month   = month
                    except Exception as e:
                        st.error(f"Report error: {e}")
                        st.session_state.current_report = _rule_based_report(state, history, currency)
            else:
                st.warning("Run at least 1 simulation month first.")
                if state:
                    st.session_state.current_report = _rule_based_report(state, history, currency)
                    st.session_state.report_month   = month

        st.markdown("</div>", unsafe_allow_html=True)

        # Key metrics snapshot
        if state:
            st.markdown("""
            <div class="fp-chart-container" style="margin-top:0.75rem;">
              <div class="fp-chart-title">Quick Metrics</div>
            """, unsafe_allow_html=True)

            metrics = [
                ("Net Worth",     format_currency(state.get("net_worth",0), currency)),
                ("Health Score",  f"{state.get('health_score',0)}/100"),
                ("Savings Rate",  f"{state.get('savings_rate',0)*100:.1f}%"),
                ("Debt",          format_currency(state.get("debt",0), currency)),
                ("Investments",   format_currency(state.get("investments",0), currency)),
                ("Month",         str(state.get("month",0))),
            ]
            for label, val in metrics:
                st.markdown(f"""
                <div style="display:flex;justify-content:space-between;
                            padding:0.35rem 0;border-bottom:1px solid rgba(0,0,0,0.04);">
                  <span style="font-size:0.78rem;color:#8888aa;">{label}</span>
                  <span style="font-size:0.82rem;font-weight:600;">{val}</span>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    with col_content:
        report = st.session_state.get("current_report")
        if report:
            st.markdown(f"""
            <div class="fp-chart-container" style="border-top:3px solid #A78BFA;">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem;">
                <div class="fp-chart-title" style="margin-bottom:0;">
                  Month {st.session_state.get('report_month',0)} Financial Report
                </div>
                <span style="font-size:0.72rem;color:#8888aa;">{datetime.now().strftime('%d %b %Y')}</span>
              </div>
            """, unsafe_allow_html=True)

            # Render report as markdown
            st.markdown(report)

            # Download button
            st.download_button(
                "Download Report (.md)",
                data=report,
                file_name=f"finpilot_report_month{st.session_state.get('report_month',0)}.md",
                mime="text/markdown",
                use_container_width=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)

            # Trend chart if history exists
            if len(history) >= 2:
                _render_trend_chart(history, currency)
        else:
            st.markdown("""
            <div class="fp-chart-container" style="text-align:center;padding:3rem;">
              <div style="font-size:2.5rem;margin-bottom:1rem;">📋</div>
              <div style="font-size:1.05rem;font-weight:600;">No report generated yet</div>
              <div style="color:#8888aa;font-size:0.85rem;margin-top:0.4rem;">
                Click "Generate AI Report" to create your personalised financial analysis.
              </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def _render_trend_chart(history, currency):
    st.markdown("""
    <div class="fp-chart-container" style="margin-top:0.75rem;">
      <div class="fp-chart-title">Full Simulation History</div>
    """, unsafe_allow_html=True)

    months = [h.get("month",i+1) for i,h in enumerate(history)]
    health = [h.get("health_score",0) for h in history]
    nw     = [h.get("net_worth",0) for h in history]

    from plotly.subplots import make_subplots
    fig = make_subplots(specs=[[{"secondary_y":True}]])
    fig.add_trace(go.Scatter(x=months,y=nw,name="Net Worth",
                              fill="tozeroy",
                              fillcolor="rgba(167,139,250,0.12)",
                              line=dict(color="#A78BFA",width=2)),
                  secondary_y=False)
    fig.add_trace(go.Scatter(x=months,y=health,name="Health Score",
                              line=dict(color="#FF6B9D",width=2,dash="dot"),
                              mode="lines+markers",marker=dict(size=4)),
                  secondary_y=True)
    fig.update_layout(height=240,margin=dict(l=0,r=0,t=10,b=0),
                       plot_bgcolor="rgba(0,0,0,0)",paper_bgcolor="rgba(0,0,0,0)",
                       legend=dict(orientation="h",y=1),
                       font=dict(family="DM Sans,sans-serif",size=11))
    fig.update_yaxes(title_text=f"Net Worth ({currency})",secondary_y=False)
    fig.update_yaxes(title_text="Health Score",range=[0,100],secondary_y=True)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
    st.markdown("</div>", unsafe_allow_html=True)


def _rule_based_report(state, history, currency):
    m    = state.get("month",0)
    nw   = format_currency(state.get("net_worth",0), currency)
    hs   = state.get("health_score",0)
    sr   = state.get("savings_rate",0)*100
    debt = format_currency(state.get("debt",0), currency)
    inv  = format_currency(state.get("investments",0), currency)

    return f"""## FinPilot AI — Month {m} Financial Report
*Generated: {datetime.now().strftime('%d %B %Y')}*

---

### Executive Summary
Your financial health score is **{hs}/100** — {'excellent progress!' if hs>=70 else 'room for improvement.' if hs>=50 else 'needs attention.'}
Net worth stands at **{nw}** with a savings rate of **{sr:.1f}%**.

### Key Metrics
| Metric | Value |
|---|---|
| Net Worth | {nw} |
| Savings Rate | {sr:.1f}% |
| Outstanding Debt | {debt} |
| Investment Portfolio | {inv} |
| Health Score | {hs}/100 |

### Analysis
{'Your savings rate exceeds 20% — excellent discipline.' if sr>=20 else f'Savings rate of {sr:.1f}% is below the recommended 20%. Focus on reducing discretionary expenses.'}

{'Debt-free! Redirect those payments to investments.' if state.get('debt',0)==0 else f'Outstanding debt of {debt}. Prioritise high-interest debt using the avalanche method.'}

### Recommendations for Next Month
1. {'Increase SIP by 10% to accelerate wealth building.' if sr>=20 else 'Cut one expense category by 15% to boost savings rate.'}
2. {'Continue current investment allocation.' if state.get('investments',0)>0 else 'Start a SIP of at least 10% of income in an equity index fund.'}
3. {'Maintain emergency fund — you are well covered.' if state.get('emergency_fund_months',0)>=3 else 'Build emergency fund to 3 months of expenses as priority.'}

---
*Report generated by FinPilot AI — finpilotai.com*
"""