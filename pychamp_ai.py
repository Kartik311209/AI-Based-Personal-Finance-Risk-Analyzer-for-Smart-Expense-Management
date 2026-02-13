import openai
import os
import pandas as pd

openai.api_key = os.getenv("OPENAI_API_KEY")

class PyChampAI:
    def __init__(self, df):
        self.df = df

    def weekly_summary(self):
        weekly = self.df.groupby("Week")["Amount"].sum()
        total = weekly.iloc[-1]
        prev = weekly.iloc[-2] if len(weekly) > 1 else total
        change = ((total - prev) / prev) * 100 if prev != 0 else 0

        category = self.df.groupby("Category")["Amount"].sum().to_dict()

        return total, change, category

    def weekly_report(self):
        total, change, category = self.weekly_summary()

        prompt = f"""
Generate a professional weekly finance report.
Total spending: ₹{total}
Change from last week: {change:.2f}%
Category breakdown: {category}
Give advice in simple language.
"""

        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )

        return response.choices[0].message["content"]

