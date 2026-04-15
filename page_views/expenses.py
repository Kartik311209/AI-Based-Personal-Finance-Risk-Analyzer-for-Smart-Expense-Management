import streamlit as st
import pandas as pd
from database import load_expenses, add_expense
from utils.charts import plot_stacked_bar


CATEGORIES = ["Food", "Rent", "Utilities", "Travel", "Entertainment",
              "Education", "Health", "Shopping", "Other"]


def render_expenses(username):
    # ── Page header ──────────────────────────────────────────────────────────
    st.markdown("""
    <div class="page-header">
        <div class="page-header-title">💳 Expenses</div>
        <div class="page-header-sub">Log manual entries and review your spending history</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Add expense form ──────────────────────────────────────────────────────
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown("""
    <div class="chart-title">➕ Log New Expense</div>
    """, unsafe_allow_html=True)

    with st.form("manual_entry", clear_on_submit=True):
        c1, c2, c3, c4 = st.columns([1.2, 2, 1.5, 1.2])
        with c1:
            date_val = st.date_input("Date")
        with c2:
            desc_val = st.text_input("Description", placeholder="e.g. Swiggy Order, Metro Card...")
        with c3:
            cat_val = st.selectbox("Category", ["— Select —"] + CATEGORIES)
        with c4:
            amt_val = st.number_input("Amount (₹)", min_value=0.0, format="%.2f", step=10.0)

        st.write("")
        submitted = st.form_submit_button("💾  Save Expense", type="primary", use_container_width=False)
        if submitted:
            if cat_val != "— Select —" and amt_val > 0:
                add_expense(username, date_val.strftime("%Y-%m-%d"), cat_val, amt_val, desc_val)
                st.success("✅ Expense saved successfully!")
                st.rerun()
            else:
                st.error("Please select a valid category and enter an amount greater than zero.")

    st.markdown('</div>', unsafe_allow_html=True)
    st.write("")

    # ── Expense history ────────────────────────────────────────────────────────
    df = load_expenses(username)
    if df.empty:
        st.markdown("""
        <div class="glass-card" style="text-align:center; padding:2.5rem;">
            <div style="font-size:2.5rem; margin-bottom:0.75rem;">📋</div>
            <div style="font-size:1rem; font-weight:600; color:#f8fafc; margin-bottom:0.4rem;">No expenses logged yet</div>
            <div style="font-size:0.82rem; color:#475569;">Use the form above or import a CSV to get started.</div>
        </div>
        """, unsafe_allow_html=True)
        return

    # Stacked bar chart
    st.markdown("""
    <div class="chart-card">
        <div class="chart-title">📊 Monthly Spend by Category</div>
    """, unsafe_allow_html=True)
    st.plotly_chart(
        plot_stacked_bar(df),
        use_container_width=True,
        key="exp_stacked",
        config={"displayModeBar": False}
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # History table
    st.markdown("""
    <div class="section-label" style="margin-top:1rem;">🗂️ Transaction History</div>
    """, unsafe_allow_html=True)

    display_df = df.sort_values("date", ascending=False).copy()
    display_df["date"] = display_df["date"].dt.strftime("%d %b %Y")
    display_df["amount"] = display_df["amount"].apply(lambda x: f"₹{x:,.2f}")
    display_df = display_df.rename(columns={
        "date": "Date", "category": "Category",
        "amount": "Amount", "note": "Description"
    })

    st.dataframe(
        display_df[["Date", "Category", "Amount", "Description"]],
        hide_index=True,
        use_container_width=True,
        height=400
    )
