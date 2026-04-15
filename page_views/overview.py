import streamlit as st
import pandas as pd
from utils.charts import plot_expense_trend, plot_category_bar, plot_donut
from utils.finance_rules import calculate_health_score
from database import load_expenses


def render_overview(username):
    # ── Page header ──────────────────────────────────────────────────────────
    st.markdown("""
    <div class="page-header">
        <div class="page-header-title">🏠 Financial Overview</div>
        <div class="page-header-sub">Month-to-date dashboard · Live from your expense ledger</div>
    </div>
    """, unsafe_allow_html=True)

    df = load_expenses(username)

    if df.empty:
        st.markdown("""
        <div class="glass-card" style="text-align:center; padding:3rem;">
            <div style="font-size:3rem; margin-bottom:1rem;">📭</div>
            <div style="font-size:1.1rem; font-weight:600; color:#f8fafc; margin-bottom:0.5rem;">No expenses found</div>
            <div style="font-size:0.85rem; color:#475569;">Add manual entries or upload a CSV to see your overview.</div>
        </div>
        """, unsafe_allow_html=True)
        return

    # ── Compute metrics ───────────────────────────────────────────────────────
    total_spent   = df['amount'].sum()
    monthly_budget = 55000
    budget_used_pct = min(int(total_spent / monthly_budget * 100), 100)
    savings       = max(monthly_budget - total_spent, 0)
    cat_spend     = df.groupby('category')['amount'].sum()
    overspent_cats = int((cat_spend > (monthly_budget / max(len(cat_spend), 1) * 1.2)).sum())
    score         = calculate_health_score(total_spent, monthly_budget)

    # ── KPI Cards ─────────────────────────────────────────────────────────────
    st.markdown('<div class="section-label">📊 Key Metrics</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(f"""
        <div class="metric-card red">
            <span class="metric-icon">💸</span>
            <div class="metric-label">Total Spent</div>
            <div class="metric-value red">₹{total_spent:,.0f}</div>
            <div class="metric-delta negative">▲ 8.2% vs last month</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="metric-card blue">
            <span class="metric-icon">🎯</span>
            <div class="metric-label">Budget Used</div>
            <div class="metric-value blue">{budget_used_pct}%</div>
            <div class="metric-delta neutral">₹{total_spent:,.0f} of ₹{monthly_budget:,}</div>
            <div class="budget-bar-track">
                <div class="budget-bar-fill" style="width:{budget_used_pct}%;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        savings_delta_class = "positive" if savings > 0 else "negative"
        savings_delta_icon  = "▲" if savings > 0 else "▼"
        st.markdown(f"""
        <div class="metric-card green">
            <span class="metric-icon">🏦</span>
            <div class="metric-label">Estimated Savings</div>
            <div class="metric-value green">₹{savings:,.0f}</div>
            <div class="metric-delta {savings_delta_class}">{savings_delta_icon} 4.1% vs last month</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="metric-card orange">
            <span class="metric-icon">⚠️</span>
            <div class="metric-label">Overspent Categories</div>
            <div class="metric-value orange">{overspent_cats}</div>
            <div class="metric-delta neutral">Health Score: {score}/100</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    # ── Charts row ────────────────────────────────────────────────────────────
    left, right = st.columns([1.6, 1])

    with left:
        st.markdown("""
        <div class="chart-card">
            <div class="chart-title">📈 Expense Trend</div>
        """, unsafe_allow_html=True)
        st.plotly_chart(
            plot_expense_trend(df),
            use_container_width=True,
            key="ov_trend",
            config={"displayModeBar": False}
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown("""
        <div class="chart-card">
            <div class="chart-title">🍩 Spend by Category</div>
        """, unsafe_allow_html=True)
        st.plotly_chart(
            plot_donut(df),
            use_container_width=True,
            key="ov_donut",
            config={"displayModeBar": False}
        )
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Category breakdown bar ────────────────────────────────────────────────
    st.markdown("""
    <div class="chart-card">
        <div class="chart-title">📊 Category Breakdown</div>
    """, unsafe_allow_html=True)
    st.plotly_chart(
        plot_category_bar(df),
        use_container_width=True,
        key="ov_cat_bar",
        config={"displayModeBar": False}
    )
    st.markdown("</div>", unsafe_allow_html=True)
