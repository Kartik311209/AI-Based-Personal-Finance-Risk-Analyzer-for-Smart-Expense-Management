import streamlit as st
import pandas as pd
from database import load_expenses
from utils.finance_rules import generate_insights


ICON_MAP = {
    "alert":   ("🚨", "#f87171"),
    "tip":     ("💡", "#fbbf24"),
    "success": ("✅", "#00e599"),
    "info":    ("ℹ️",  "#38bdf8"),
}


def render_insights(username):
    # ── Page header ──────────────────────────────────────────────────────────
    st.markdown("""
    <div class="page-header">
        <div class="page-header-title">✨ AI Spending Insights</div>
        <div class="page-header-sub">Actionable recommendations powered by your transaction behaviour</div>
    </div>
    """, unsafe_allow_html=True)

    df = load_expenses(username)

    # Summary pill row
    if not df.empty:
        total   = df['amount'].sum()
        n_txns  = len(df)
        n_cats  = df['category'].nunique()
        c1, c2, c3, _ = st.columns([1, 1, 1, 2])
        with c1:
            st.markdown(f"""
            <div class="metric-card green" style="padding:1rem;">
                <div class="metric-label">Total Analysed</div>
                <div class="metric-value green" style="font-size:1.4rem;">₹{total:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="metric-card blue" style="padding:1rem;">
                <div class="metric-label">Transactions</div>
                <div class="metric-value blue" style="font-size:1.4rem;">{n_txns}</div>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class="metric-card purple" style="padding:1rem;">
                <div class="metric-label">Categories</div>
                <div class="metric-value" style="font-size:1.4rem; color:#a78bfa;">{n_cats}</div>
            </div>
            """, unsafe_allow_html=True)

        st.write("")

    insights = generate_insights(df)
    st.markdown('<div class="section-label">🧠 Insights</div>', unsafe_allow_html=True)

    for idx, item in enumerate(insights):
        if isinstance(item, dict):
            i_type  = item.get("type", "info")
            icon, color = ICON_MAP.get(i_type, ("ℹ️", "#38bdf8"))

            # Convert markdown bold to HTML
            text_html = item.get("text", "").replace(
                "\n", "<br/>"
            )
            import re
            text_html = re.sub(r'\*\*(.+?)\*\*', r'<strong style="color:#e2e8f0;">\1</strong>', text_html)

            st.markdown(f"""
            <div class="insight-card {i_type}" style="animation-delay:{idx * 0.08}s;">
                <div class="insight-title" style="color:{color};">
                    {icon}&nbsp; {item.get('title', '')}
                </div>
                <div class="insight-text">{text_html}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="insight-card info">
                <div class="insight-text">ℹ️ {item}</div>
            </div>
            """, unsafe_allow_html=True)
