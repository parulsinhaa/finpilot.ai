"""
FinPilot AI — Calculator Hub
EMI, SIP, Compound Growth, Net Worth, Emergency Fund, Debt Payoff, Inflation.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from app.calculators import (
    emi, emi_amortisation, sip_future_value, sip_growth_series,
    compound_growth, inflation_adjusted_value, net_worth as calc_net_worth,
    emergency_fund_required, debt_payoff_avalanche, debt_payoff_snowball,
    inflation_projection, goal_monthly_saving,
)
from backend.currency import format_currency


def render_calculators():
    st.markdown("""
    <div class="fp-fade-in">
    <h2 style="font-family:'Bricolage Grotesque',sans-serif;font-weight:700;
               letter-spacing:-0.03em;margin-bottom:0.25rem;">Calculator Hub</h2>
    <p style="color:#8888aa;margin-bottom:1.5rem;">
        All financial calculators integrated into your simulation engine.
    </p>
    """, unsafe_allow_html=True)

    currency = st.session_state.get("currency","INR")
    sym = {"INR":"₹","USD":"$","EUR":"€","GBP":"£","AED":"د.إ"}.get(currency, currency)

    tabs = st.tabs([
        "EMI", "SIP", "Compound Growth",
        "Net Worth", "Emergency Fund", "Debt Payoff", "Inflation", "Goal Planner"
    ])

    # ── EMI ──────────────────────────────────────────────────────────────────
    with tabs[0]:
        st.markdown("### EMI Calculator")
        col1, col2, col3 = st.columns(3)
        with col1:
            principal = st.number_input(f"Loan Amount ({sym})", min_value=0.0,
                                         value=500000.0, step=10000.0, key="emi_p")
        with col2:
            rate = st.number_input("Annual Interest Rate (%)", min_value=0.0,
                                    value=9.5, step=0.1, key="emi_r")
        with col3:
            months = st.number_input("Loan Tenure (months)", min_value=1,
                                      value=60, step=6, key="emi_m")

        if st.button("Calculate EMI", type="primary", key="calc_emi"):
            result = emi(principal, rate, months)
            _render_result_cards([
                ("Monthly EMI",    format_currency(result["emi"], currency)),
                ("Total Payment",  format_currency(result["total_payment"], currency)),
                ("Total Interest", format_currency(result["total_interest"], currency)),
                ("Principal",      format_currency(result["principal"], currency)),
            ])
            # Amortisation chart
            schedule = emi_amortisation(principal, rate, months)
            df = pd.DataFrame(schedule)
            fig = go.Figure()
            fig.add_trace(go.Bar(x=df["month"], y=df["principal_paid"],
                                  name="Principal", marker_color="#A78BFA"))
            fig.add_trace(go.Bar(x=df["month"], y=df["interest_paid"],
                                  name="Interest", marker_color="#FF6B9D"))
            fig.update_layout(barmode="stack", height=260,
                               margin=dict(l=0,r=0,t=10,b=0),
                               plot_bgcolor="rgba(0,0,0,0)",paper_bgcolor="rgba(0,0,0,0)",
                               xaxis_title="Month",yaxis_title=f"Amount ({currency})",
                               legend=dict(orientation="h",y=1),
                               font=dict(family="DM Sans,sans-serif",size=11))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

    # ── SIP ──────────────────────────────────────────────────────────────────
    with tabs[1]:
        st.markdown("### SIP Calculator")
        col1, col2, col3 = st.columns(3)
        with col1:
            monthly = st.number_input(f"Monthly SIP ({sym})", 100.0, 1000000.0,
                                       5000.0, 500.0, key="sip_m")
        with col2:
            annual_ret = st.number_input("Expected Annual Return (%)", 1.0, 40.0,
                                          12.0, 0.5, key="sip_r")
        with col3:
            years = st.number_input("Investment Period (years)", 1, 40, 10, 1, key="sip_y")

        result = sip_future_value(monthly, annual_ret, years)
        series = sip_growth_series(monthly, annual_ret, years)

        _render_result_cards([
            ("Future Value",    format_currency(result["future_value"], currency)),
            ("Total Invested",  format_currency(result["total_invested"], currency)),
            ("Total Returns",   format_currency(result["total_returns"], currency)),
            ("Wealth Ratio",    f"{result['wealth_ratio']:.2f}x"),
        ])

        df = pd.DataFrame(series)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["year"], y=df["value"], name="Portfolio Value",
                                  fill="tozeroy",
                                  fillcolor="rgba(167,139,250,0.15)",
                                  line=dict(color="#A78BFA", width=2.5)))
        fig.add_trace(go.Scatter(x=df["year"], y=df["invested"], name="Amount Invested",
                                  line=dict(color="#FF6B9D", width=2, dash="dot")))
        fig.update_layout(height=260, margin=dict(l=0,r=0,t=10,b=0),
                           plot_bgcolor="rgba(0,0,0,0)",paper_bgcolor="rgba(0,0,0,0)",
                           legend=dict(orientation="h",y=1),
                           font=dict(family="DM Sans,sans-serif",size=11))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

    # ── Compound Growth ───────────────────────────────────────────────────────
    with tabs[2]:
        st.markdown("### Compound Growth Calculator")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            cp = st.number_input(f"Principal ({sym})", 0.0, 10000000.0, 100000.0, 10000.0, key="cg_p")
        with col2:
            cr = st.number_input("Annual Rate (%)", 0.0, 50.0, 8.0, 0.5, key="cg_r")
        with col3:
            cy = st.number_input("Years", 1, 50, 10, 1, key="cg_y")
        with col4:
            comp = st.selectbox("Compounding", ["monthly","quarterly","annually","daily"], key="cg_c")

        result = compound_growth(cp, cr, cy, comp)
        _render_result_cards([
            ("Future Value",    format_currency(result["future_value"], currency)),
            ("Total Interest",  format_currency(result["total_interest"], currency)),
            ("Principal",       format_currency(result["principal"], currency)),
            ("Effective Rate",  f"{result['effective_rate']:.3f}%"),
        ])

    # ── Net Worth ─────────────────────────────────────────────────────────────
    with tabs[3]:
        st.markdown("### Net Worth Calculator")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Assets**")
            savings    = st.number_input(f"Savings ({sym})", 0.0, value=200000.0, key="nw_sav")
            invest     = st.number_input(f"Investments ({sym})", 0.0, value=150000.0, key="nw_inv")
            property_v = st.number_input(f"Property ({sym})", 0.0, value=0.0, key="nw_prop")
            other_a    = st.number_input(f"Other Assets ({sym})", 0.0, value=0.0, key="nw_oa")
        with col2:
            st.markdown("**Liabilities**")
            home_loan  = st.number_input(f"Home Loan ({sym})", 0.0, value=0.0, key="nw_hl")
            car_loan   = st.number_input(f"Car Loan ({sym})", 0.0, value=50000.0, key="nw_cl")
            personal_l = st.number_input(f"Personal Loan ({sym})", 0.0, value=30000.0, key="nw_pl")
            cc         = st.number_input(f"Credit Card ({sym})", 0.0, value=10000.0, key="nw_cc")

        assets = {"savings":savings,"investments":invest,"property":property_v,"other":other_a}
        liabilities = {"home_loan":home_loan,"car_loan":car_loan,
                        "personal_loan":personal_l,"credit_card":cc}
        result = calc_net_worth(assets, liabilities)

        nw_val = result["net_worth"]
        nw_color = "#10b981" if nw_val >= 0 else "#ef4444"
        st.markdown(f"""
        <div style="text-align:center;padding:1.5rem;background:var(--bg-card,#fff);
                    border-radius:20px;margin:1rem 0;border:2px solid {nw_color}20;">
          <div style="font-size:0.8rem;color:#8888aa;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:4px;">Your Net Worth</div>
          <div style="font-family:'Bricolage Grotesque',sans-serif;font-size:2.5rem;font-weight:700;color:{nw_color};">
            {format_currency(nw_val, currency)}
          </div>
          <div style="font-size:0.82rem;color:#8888aa;margin-top:4px;">
            DTI Ratio: {result['debt_to_asset_ratio']*100:.1f}%
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Donut chart
        fig = go.Figure(go.Pie(
            labels=["Assets","Liabilities"],
            values=[result["total_assets"], result["total_liabilities"]],
            hole=0.6,
            marker_colors=["#A78BFA","#FF6B9D"],
        ))
        fig.update_layout(height=220, margin=dict(l=0,r=0,t=0,b=0),
                           paper_bgcolor="rgba(0,0,0,0)",showlegend=True,
                           legend=dict(orientation="h",y=-0.1))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

    # ── Emergency Fund ────────────────────────────────────────────────────────
    with tabs[4]:
        st.markdown("### Emergency Fund Calculator")
        col1, col2, col3 = st.columns(3)
        with col1:
            exp = st.number_input(f"Monthly Expenses ({sym})", 0.0, value=40000.0, key="ef_e")
        with col2:
            stab = st.selectbox("Job Stability", ["very_stable","stable","moderate","unstable"], index=1, key="ef_s")
        with col3:
            dep = st.checkbox("Have Dependents?", key="ef_d")

        result = emergency_fund_required(exp, job_stability=stab, has_dependents=dep)
        _render_result_cards([
            ("Recommended Fund",  format_currency(result["recommended_amount"], currency)),
            ("Minimum Fund",      format_currency(result["minimum_amount"], currency)),
            ("Months Coverage",   f"{result['recommended_months']} months"),
            ("Monthly Expenses",  format_currency(result["monthly_expenses"], currency)),
        ])
        st.info(f"Rationale: {result['rationale']}")

    # ── Debt Payoff ───────────────────────────────────────────────────────────
    with tabs[5]:
        st.markdown("### Debt Payoff Planner")
        st.markdown("Add your debts below:")

        if "debts" not in st.session_state:
            st.session_state.debts = [
                {"name":"Personal Loan","balance":150000,"rate":14.0,"min_payment":5000},
                {"name":"Credit Card","balance":50000,"rate":36.0,"min_payment":2500},
            ]

        debts = st.session_state.debts
        for i, debt in enumerate(debts):
            c1,c2,c3,c4,c5 = st.columns([2,2,1.5,2,0.5])
            with c1: debt["name"]        = st.text_input("Name",debt["name"],key=f"dn{i}")
            with c2: debt["balance"]     = st.number_input(f"Balance ({sym})",0.0,value=float(debt["balance"]),key=f"db{i}")
            with c3: debt["rate"]        = st.number_input("Rate%",0.0,50.0,float(debt["rate"]),key=f"dr{i}")
            with c4: debt["min_payment"] = st.number_input(f"Min Pay ({sym})",0.0,value=float(debt["min_payment"]),key=f"dm{i}")
            with c5:
                if st.button("✕",key=f"dd{i}"):
                    st.session_state.debts.pop(i); st.rerun()

        if st.button("+ Add Debt"):
            st.session_state.debts.append({"name":"New Debt","balance":50000,"rate":12.0,"min_payment":2000})
            st.rerun()

        extra = st.number_input(f"Extra Monthly Payment ({sym})", 0.0, value=5000.0, key="dp_extra")

        if st.button("Compare Avalanche vs Snowball", type="primary", key="calc_debt"):
            aval = debt_payoff_avalanche(debts, extra)
            snow = debt_payoff_snowball(debts, extra)
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Avalanche Method** (pay highest rate first)")
                _render_result_cards([
                    ("Months to Payoff", str(aval["months_to_payoff"])),
                    ("Total Interest",   format_currency(aval["total_interest"], currency)),
                ])
            with col2:
                st.markdown("**Snowball Method** (pay smallest balance first)")
                _render_result_cards([
                    ("Months to Payoff", str(snow["months_to_payoff"])),
                    ("Total Interest",   format_currency(snow["total_interest"], currency)),
                ])
            saved = snow["total_interest"] - aval["total_interest"]
            if saved > 0:
                st.success(f"Avalanche saves you {format_currency(saved,currency)} in interest over Snowball.")

    # ── Inflation ──────────────────────────────────────────────────────────────
    with tabs[6]:
        st.markdown("### Inflation-Adjusted Projections")
        col1, col2, col3 = st.columns(3)
        with col1:
            ia = st.number_input(f"Current Amount ({sym})", 0.0, value=1000000.0, key="ia_a")
        with col2:
            ig = st.number_input("Annual Growth Rate (%)", 0.0, 50.0, 8.0, 0.5, key="ia_g")
        with col3:
            ii = st.number_input("Inflation Rate (%)", 0.0, 30.0, 6.0, 0.5, key="ia_i")
        iy = st.slider("Years", 1, 30, 10, key="ia_y")

        series = inflation_projection(ia, ig, ii, iy)
        df = pd.DataFrame(series)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["year"], y=df["nominal"], name="Nominal Value",
                                  line=dict(color="#A78BFA",width=2.5)))
        fig.add_trace(go.Scatter(x=df["year"], y=df["real"], name="Real Value (after inflation)",
                                  line=dict(color="#FF6B9D",width=2,dash="dot")))
        fig.update_layout(height=280, margin=dict(l=0,r=0,t=10,b=0),
                           plot_bgcolor="rgba(0,0,0,0)",paper_bgcolor="rgba(0,0,0,0)",
                           legend=dict(orientation="h",y=1),
                           font=dict(family="DM Sans,sans-serif",size=11))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

        final = series[-1] if series else {}
        _render_result_cards([
            ("Nominal Value",     format_currency(final.get("nominal",0), currency)),
            ("Real Value",        format_currency(final.get("real",0), currency)),
            ("Inflation Erosion", format_currency(final.get("inflation_erosion",0), currency)),
        ])

    # ── Goal Planner ──────────────────────────────────────────────────────────
    with tabs[7]:
        st.markdown("### Goal-Based Savings Planner")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            gt = st.number_input(f"Target Amount ({sym})", 0.0, value=1000000.0, key="gp_t")
        with col2:
            gc = st.number_input(f"Current Savings ({sym})", 0.0, value=50000.0, key="gp_c")
        with col3:
            gr = st.number_input("Expected Return (%)", 0.0, 30.0, 12.0, 0.5, key="gp_r")
        with col4:
            gy = st.number_input("Years to Goal", 1, 30, 5, 1, key="gp_y")

        result = goal_monthly_saving(gt, gc, gr, gy)
        if result.get("already_reached"):
            st.success(f"You have already reached your target of {format_currency(gt,currency)}!")
        else:
            _render_result_cards([
                ("Monthly Saving Needed", format_currency(result["monthly_saving"], currency)),
                ("Gap to Target",         format_currency(result["gap"], currency)),
                ("Target Amount",         format_currency(result["target"], currency)),
                ("Annual Return",         f"{result['annual_return']}%"),
            ])

    st.markdown("</div>", unsafe_allow_html=True)


def _render_result_cards(items: list):
    cols = st.columns(len(items))
    for col, (label, value) in zip(cols, items):
        with col:
            st.markdown(f"""
            <div class="fp-metric">
              <div class="fp-metric-label">{label}</div>
              <div class="fp-metric-value" style="font-size:1.3rem;">{value}</div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)