import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from expense_db import add_expense, get_expenses
from finance_ai import clean_data, category_analysis, financial_advice
from ml_model import predict_next_month
from fintech_ai import budget_planner, overspending_alert, savings_target, weekly_trend
import plotly.graph_objects as go

def finance_app():
    st.subheader("💎 PyChamp Daily Expense Tracker + AI")

    # 📝 Add Expense Form
    st.write("## ➕ Add Daily Expense")

    with st.form("expense_form"):
        date = st.date_input("Date")
        category = st.selectbox("Category", ["Food 🍔", "Travel 🚕", "Shopping 🛍️", "Bills 💡", "Entertainment 🎬", "Other"])
        description = st.text_input("Description")
        amount = st.number_input("Amount ₹", min_value=0.0, step=1.0)

        submitted = st.form_submit_button("Add Expense 💾")

        if submitted:
            add_expense(str(date), category, description, amount)
            st.success("✅ Expense added successfully!")
            st.rerun()

    # 📊 Show All Expenses
    st.write("## 📋 Your Expenses")

    data = get_expenses()
    df = pd.DataFrame(data, columns=["Date", "Category", "Description", "Amount"])

    if df.empty:
        st.info("No expenses added yet.")
        return

    st.dataframe(df)

    # Convert for AI
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")

    # 💰 Total Expense
    total = df["Amount"].sum()
    st.metric("💰 Total Expense", f"₹{round(total,2)}")

    # ⚠️ Overspending Alerts
    alerts = overspending_alert(df)
    if not alerts.empty:
        st.error("🚨 Overspending Detected!")
        st.write(alerts)
    else:
        st.success("✅ Spending under control")

    # 🧠 Budget Planner
    st.write("### 🧠 Smart Budget Planner")
    budget_df, _ = budget_planner(df)
    st.dataframe(budget_df)

    # 💡 Savings Target
    target = savings_target(df)
    st.metric("💰 Suggested Savings", f"₹{target}")

    # 📊 weekly Trend
    import plotly.graph_objects as go

    st.write("### 📈 Weekly Stock-Style Interactive Chart")

    trend = weekly_trend(df)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
      x=trend.index.astype(str),
      y=trend.values,
      mode="lines+markers",
      name="Weekly Expense",
      line=dict(width=3)
  ))

    fig.add_trace(go.Scatter(
    x=trend.index.astype(str),
    y=pd.Series(trend.values).rolling(3).mean(),
    mode="lines",
    name="Moving Average",
    line=dict(dash="dash")
))

    fig.update_layout(
    title="📊 Weekly Expense Trend (Fintech Style)",
    xaxis_title="Week",
    yaxis_title="Amount (₹)",
    template="plotly_dark"   # stock market vibe 😎
)

    st.plotly_chart(fig, use_container_width=True)

    # ⚠️ Risk Analysis
    summary, _ = category_analysis(df)
    st.write("### ⚠️ Risk Analysis")
    st.dataframe(summary[["Category", "Percent", "Risk"]])

    # 🤖 AI Advice
    st.write("### 🤖 PyChamp AI Advice")
    st.info(financial_advice(summary))

    # 🔮 ML Prediction
    pred = predict_next_month(df)
    st.success(f"🔮 Next Month Expense Prediction: ₹{pred}")



