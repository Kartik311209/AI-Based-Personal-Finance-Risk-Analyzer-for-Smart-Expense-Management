import pandas as pd
import numpy as np

def clean_data(df):
    df.columns = df.columns.str.strip()

    col_map = {}
    for col in df.columns:
        c = col.lower()
        if "amount" in c:
            col_map["Amount"] = col
        if "category" in c or "type" in c:
            col_map["Category"] = col
        if "date" in c:
            col_map["Date"] = col

    df = df.rename(columns={v:k for k,v in col_map.items()})
    return df


def category_analysis(df):
    summary = df.groupby("Category")["Amount"].sum().reset_index()
    total = summary["Amount"].sum()
    summary["Percent"] = (summary["Amount"] / total) * 100

    avg_percent = summary["Percent"].mean()

    def risk_level(p):
        if p > avg_percent * 1.5:
            return "High Risk 🔴"
        elif p > avg_percent:
            return "Medium Risk 🟡"
        else:
            return "Low Risk 🟢"

    summary["Risk"] = summary["Percent"].apply(risk_level)
    return summary, total


def financial_advice(summary):
    high_risk = summary[summary["Risk"] == "High Risk 🔴"]

    if high_risk.empty:
        return "✅ Your spending is balanced. Keep it up! 💪"

    advice = "⚠️ Reduce spending in:\n"
    for _, row in high_risk.iterrows():
        advice += f"• {row['Category']} ({round(row['Percent'],2)}%)\n"

    return advice