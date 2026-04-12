"""
Core financial logic, budgeting rules, and scoring engines.
"""

def calculate_health_score(total_spent, monthly_budget=50000):
    """Returns a health score out of 100 based on spending vs budget."""
    if total_spent == 0:
        return 100
    
    utilization = total_spent / monthly_budget
    if utilization <= 0.5:
        score = 95
    elif utilization <= 0.8:
        score = 80 - int((utilization - 0.5) * 50)
    elif utilization <= 1.0:
        score = 60 - int((utilization - 0.8) * 100)
    else:
        score = max(10, 40 - int((utilization - 1.0) * 50))
        
    return score

def get_health_status(score):
    if score >= 80:
        return "Excellent", "#00e599"
    elif score >= 60:
        return "Good — room to improve", "#0ea5e9"
    elif score >= 40:
        return "Warning — near budget limit", "#eab308"
    else:
        return "Critical — overspent", "#ef4444"

def generate_insights(df):
    """Generates a list of actionable text insights based on spending data."""
    if df.empty or "amount" not in df.columns or "category" not in df.columns:
        return [{"type": "info", "title": "Welcome to AI Insights", "text": "Start by adding some manual expenses or uploading a CSV. The AI needs transaction histories to analyze your spending behavior."}]

    insights = []
    total = df["amount"].sum()
    
    if total <= 0:
        return [{"type": "info", "title": "Zero Expenses", "text": "Your total spend is zero. Good job!"}]

    cat_spend = df.groupby("category")["amount"].sum().sort_values(ascending=False)
    if cat_spend.empty:
        return [{"type": "info", "title": "Categorize Data", "text": "Please make sure your expenses have valid categories."}]
        
    top_cat = cat_spend.index[0]
    top_val = cat_spend.iloc[0]

    # Rule 1: High concentration warning
    if top_val > total * 0.4:
        insights.append({
            "type": "alert",
            "title": f"High concentration in {top_cat}",
            "text": f"You spend **{int(top_val/total*100)}%** of your money on {top_cat}. Try capping it to maintain a balanced budget."
        })
        
    # Rule 2: Wastage vs Study/Coaching Rule (The specific user request)
    # Define what is "Good Investment"
    exempt_keywords = ["study", "coaching", "education", "course", "rent", "utilities", "bills", "medical", "health"]
    
    # Calculate discretionary spend (potential wastage) - case insensitive check
    wastage_df = df[~df["category"].str.lower().isin(exempt_keywords)]
    
    if not wastage_df.empty:
        wastage_cats = wastage_df.groupby("category")["amount"].sum().sort_values(ascending=False)
        top_wastage_cat = wastage_cats.index[0]
        top_wastage_amt = wastage_cats.iloc[0]
        
        insights.append({
            "type": "tip",
            "title": "Stop the Wastage! 🛑",
            "text": f"Bhai, expenses on **'{top_wastage_cat}'** are running high (₹{top_wastage_amt:,.0f}). Aapko paise strictly unnumerable wastage par kam karne hain.\n\n*Note: Expenses on 'Study' and 'Coaching' are treated as solid investments for your future and immune from cuts, but you MUST cut down this '{top_wastage_cat}' wastage by 20% to boost your savings!*"
        })
    else:
        # If user ONLY spends on study or rent, praise them!
        insights.append({
            "type": "success",
            "title": "Excellent Financial Discipline 🎯",
            "text": "Bhai, you have zero recorded 'wastage' expenses! All your current spending is on essential items like Study, Coaching, and Bills. Keep up this amazing mindset!"
        })
    
    # Rule 3: Needs vs Wants (50-30-20 rough estimate)
    insights.append({
        "type": "info",
        "title": "Ideal 50/30/20 Budget Formula",
        "text": f"Based on your total spend of ₹{total:,.0f}, your target allocation should ideally be: \n- **Needs:** ₹{total*0.5:,.0f}\n- **Wants:** ₹{total*0.3:,.0f}\n- **Savings:** ₹{total*0.2:,.0f}."
    })

    return insights
