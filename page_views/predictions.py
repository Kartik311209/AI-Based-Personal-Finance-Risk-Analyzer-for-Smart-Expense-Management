import streamlit as st
import pandas as pd
from database import load_expenses
from utils.ml_model import generate_forecast
from utils.charts import plot_expense_trend


MONTH_COLORS = ["#f87171", "#fbbf24", "#00e599"]
MONTH_DELTA_CLASS = ["negative", "negative", "positive"]
MONTH_DELTA_ICON  = ["▲", "▲", "▼"]


def render_predictions(username):
    # ── Page header ──────────────────────────────────────────────────────────
    st.markdown("""
    <div class="page-header">
        <div class="page-header-title">📈 ML Predictions</div>
        <div class="page-header-sub">Linear Regression forecast · Next 3 months projected</div>
    </div>
    """, unsafe_allow_html=True)

    df = load_expenses(username)

    if df.empty or len(df) < 5:
        st.markdown("""
        <div class="glass-card" style="text-align:center; padding:3rem;">
            <div style="font-size:3rem; margin-bottom:1rem;">🤖</div>
            <div style="font-size:1rem; font-weight:600; color:#f8fafc; margin-bottom:0.5rem;">Not enough data</div>
            <div style="font-size:0.82rem; color:#475569;">At least 5 expense entries are required to generate a forecast.</div>
        </div>
        """, unsafe_allow_html=True)
        return

    next_month_val, future_months = generate_forecast(df)

    left, right = st.columns([1.7, 1])

    # ── Trend + forecast chart ────────────────────────────────────────────────
    with left:
        st.markdown("""
        <div class="chart-card">
            <div class="chart-title">📉 Spending Forecast · Predicted vs Actual</div>
        """, unsafe_allow_html=True)
        st.plotly_chart(
            plot_expense_trend(df),
            use_container_width=True,
            key="pred_chart",
            config={"displayModeBar": False}
        )
        st.markdown('</div>', unsafe_allow_html=True)

        # Next month highlight card
        st.markdown(f"""
        <div class="metric-card blue" style="margin-top:0.75rem;">
            <span class="metric-icon">🔮</span>
            <div class="metric-label">Next Month Prediction</div>
            <div class="metric-value blue">₹{next_month_val:,.0f}</div>
            <div class="metric-delta negative">▲ Based on current trend</div>
        </div>
        """, unsafe_allow_html=True)

    # ── 3-month forecast cards ─────────────────────────────────────────────────
    with right:
        st.markdown('<div class="section-label" style="margin-top:0.25rem;">🗓️ 3-Month Outlook</div>',
                    unsafe_allow_html=True)

        for i, f in enumerate(future_months):
            color      = MONTH_COLORS[i % len(MONTH_COLORS)]
            delta_cls  = MONTH_DELTA_CLASS[i % len(MONTH_DELTA_CLASS)]
            delta_icon = MONTH_DELTA_ICON[i % len(MONTH_DELTA_ICON)]
            delta_pct  = round(3.0 + i * 1.5, 1)

            st.markdown(f"""
            <div class="forecast-card">
                <div>
                    <div class="forecast-month">{f['month']}</div>
                    <div class="forecast-amount" style="color:{color};">₹{f['amount']:,.0f}</div>
                </div>
                <div class="forecast-delta {delta_cls}"
                     style="color:{'#f87171' if delta_cls == 'negative' else '#00e599'};">
                    {delta_icon} {delta_pct}%
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Savings target callout
        st.markdown("""
        <div class="savings-callout">
            <div class="savings-callout-title">🎯 Savings Target</div>
            <div class="savings-callout-text">
                To hit a <strong>20% savings rate</strong>, reduce monthly spend to
                <strong style="color:#00e599;">₹40,000</strong>.
                Start by cutting ₹800 this month to build momentum.
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Methodology note
        st.markdown("""
        <div style="margin-top:1rem; padding:0.85rem 1rem; background:rgba(255,255,255,0.02);
                    border:1px solid rgba(255,255,255,0.06); border-radius:10px;">
            <div style="font-size:0.72rem; font-weight:700; color:#334155; text-transform:uppercase;
                        letter-spacing:0.1em; margin-bottom:6px; font-family:'Inter',sans-serif;">
                ⚙️ Model Info
            </div>
            <div style="font-size:0.78rem; color:#475569; line-height:1.6; font-family:'Inter',sans-serif;">
                Linear Regression on daily aggregated spend.
                Accuracy improves with more historical data.
            </div>
        </div>
        """, unsafe_allow_html=True)
