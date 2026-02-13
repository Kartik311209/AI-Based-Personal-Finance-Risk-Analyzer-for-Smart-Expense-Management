import numpy as np

def detect_risk(df):
    total = df["Amount"].sum()
    category_sum = df.groupby("Category")["Amount"].sum()
    
    risk = {}
    for cat, amt in category_sum.items():
        percent = (amt / total) * 100
        if percent > 40:
            risk[cat] = "HIGH RISK"
        elif percent > 25:
            risk[cat] = "MODERATE RISK"
        else:
            risk[cat] = "LOW RISK"
    
    return risk


def advanced_risk_score(df, income=50000):
    total_expense = df["Amount"].sum()
    ratio = total_expense / income
    
    category_ratio = df.groupby("Category")["Amount"].sum() / total_expense
    concentration_risk = category_ratio.max()
    
    score = 100 - ((ratio * 60) + (concentration_risk * 40)) * 100
    return max(0, round(score, 2))
