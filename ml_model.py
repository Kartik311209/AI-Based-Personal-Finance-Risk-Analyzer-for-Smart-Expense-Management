import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np

def train_model(df):
    # Ensure Date column exists
    if "Date" not in df.columns:
        return None, "❌ Date column missing"

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Month"] = df["Date"].dt.month
    df["Year"] = df["Date"].dt.year

    # Features (X) and Target (y)
    X = df[["Month", "Year"]]
    y = df["Amount"]

    model = LinearRegression()
    model.fit(X, y)

    return model, None


def predict_next_month(df):
    model, error = train_model(df)
    if error:
        return error

    last_date = pd.to_datetime(df["Date"]).max()
    next_month = last_date.month + 1
    year = last_date.year

    if next_month > 12:
        next_month = 1
        year += 1

    prediction = model.predict([[next_month, year]])[0]
    return round(prediction, 2)