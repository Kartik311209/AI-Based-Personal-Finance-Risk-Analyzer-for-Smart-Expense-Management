import pandas as pd
import numpy as np

def budget_planner(df):
    total = df["Amount"].sum()
    categories = df.groupby("Category")["Amount"].sum().reset_index()

    # Ideal budget rule (50-30-20 logic)
    ideal_ratio = 0.5  # needs
    luxury_ratio = 0.3
    savings_ratio = 0.2

    avg = categories["Amount"].mean()

    categories["Type"] = categories["Amount"].apply(
        lambda x: "Luxury 💎" if x > avg else "Need 🏠"
    )

    categories["Recommended"] = categories["Amount"].apply(
        lambda x: x * 0.7 if x > avg else x * 1.05
    )

    return categories, total


def overspending_alert(df):
    categories = df.groupby("Category")["Amount"].sum()
    avg = categories.mean()

    alerts = categories[categories > avg * 1.4]

    return alerts


def savings_target(df):
    total = df["Amount"].sum()
    target = total * 0.2
    return round(target, 2)


def weekly_trend(df):
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    weekly = df.groupby(df["Date"].dt.to_period("M"))["Amount"].sum()
    return weekly
