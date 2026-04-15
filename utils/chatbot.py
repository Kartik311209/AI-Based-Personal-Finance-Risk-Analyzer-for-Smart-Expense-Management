"""
PyChamp AI Finance Chatbot Engine
===================================
Rule-based NLP chatbot that acts as a smart financial advisor.
Analyzes a pandas DataFrame of expenses and gives actionable advice.

DataFrame schema expected:
    - date     : datetime-like
    - category : str
    - amount   : float
    - note     : str (optional)
"""

import re
import random
import pandas as pd
from datetime import datetime


# ─────────────────────────────────────────────────────────────────────────────
# Constants / Configs
# ─────────────────────────────────────────────────────────────────────────────

ESSENTIAL_CATEGORIES = {
    "rent", "utilities", "bills", "electricity", "water",
    "study", "education", "coaching", "course", "tuition",
    "medical", "health", "pharmacy", "doctor", "insurance",
    "groceries", "grocery"
}

SAVINGS_TIPS = [
    "Try the 24-hour rule: wait a day before any non-essential purchase.",
    "Automate a fixed savings transfer on the 1st of every month.",
    "Cook 3 extra meals at home per week — that alone can save ₹1,500+ monthly.",
    "Cancel subscriptions you haven't used in the last 30 days.",
    "Use the 50/30/20 rule: 50% needs, 30% wants, 20% savings.",
    "Track every expense in real time — awareness alone cuts spending by 15%.",
    "Buy in bulk for recurring household items to reduce per-unit cost.",
    "Set a weekly 'no-spend' day to build a savings habit.",
]

GREETINGS = ["hi", "hello", "hey", "heyy", "yo", "sup", "what's up", "namaste"]
FAREWELLS = ["bye", "goodbye", "see ya", "later", "quit", "exit", "close"]


# ─────────────────────────────────────────────────────────────────────────────
# Core Analytics Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _total_spent(df: pd.DataFrame) -> float:
    return float(df["amount"].sum()) if not df.empty else 0.0


def _category_breakdown(df: pd.DataFrame) -> pd.Series:
    if df.empty:
        return pd.Series(dtype=float)
    return df.groupby("category")["amount"].sum().sort_values(ascending=False)


def _top_category(df: pd.DataFrame):
    breakdown = _category_breakdown(df)
    if breakdown.empty:
        return None, 0.0
    return breakdown.index[0], float(breakdown.iloc[0])


def _discretionary_spend(df: pd.DataFrame) -> pd.Series:
    """Non-essential categories only."""
    if df.empty:
        return pd.Series(dtype=float)
    mask = ~df["category"].str.lower().isin(ESSENTIAL_CATEGORIES)
    return df[mask].groupby("category")["amount"].sum().sort_values(ascending=False)


def _monthly_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or "date" not in df.columns:
        return pd.DataFrame()
    temp = df.copy()
    temp["month"] = pd.to_datetime(temp["date"]).dt.to_period("M").astype(str)
    return temp.groupby("month")["amount"].sum().reset_index().rename(columns={"amount": "total"})


def _savings_potential(df: pd.DataFrame, cut_pct: float = 0.20) -> float:
    disc = _discretionary_spend(df)
    return float(disc.sum() * cut_pct)


def _health_score(df: pd.DataFrame, budget: float = 50000) -> int:
    total = _total_spent(df)
    if total == 0:
        return 100
    ratio = total / budget
    if ratio <= 0.5:
        return 95
    elif ratio <= 0.8:
        return 80 - int((ratio - 0.5) * 50)
    elif ratio <= 1.0:
        return 60 - int((ratio - 0.8) * 100)
    return max(10, 40 - int((ratio - 1.0) * 50))


def _format_inr(amount: float) -> str:
    return f"₹{amount:,.0f}"


# ─────────────────────────────────────────────────────────────────────────────
# Intent Detection
# ─────────────────────────────────────────────────────────────────────────────

INTENT_PATTERNS = {
    "total_spend": [
        r"how much.*(spend|spent|expense)",
        r"total.*(spend|spent|expense|amount)",
        r"(what|tell).*(spend|spent|total)",
        r"kitna.*kharch",
        r"my.*expense",
        r"expense.*total",
    ],
    "top_category": [
        r"highest.*(category|spend|expense)",
        r"top.*(category|spend|expense)",
        r"most.*(spent|expense|money)",
        r"where.*(money|spend|going)",
        r"which.*(category|area|head)",
        r"maximum.*spend",
    ],
    "savings_advice": [
        r"how.*save",
        r"saving.*plan",
        r"savings.*tip",
        r"reduce.*expense",
        r"cut.*expense",
        r"save.*money",
        r"bachana.*paisa",
        r"tips.*save",
        r"suggest.*saving",
    ],
    "spending_pattern": [
        r"pattern",
        r"trend",
        r"monthly.*spend",
        r"spending.*habit",
        r"analysis",
        r"analyze",
        r"breakdown",
        r"distribution",
    ],
    "reduce_expense": [
        r"reduce",
        r"cut back",
        r"decrease",
        r"lower.*expense",
        r"spend.*less",
        r"minimize",
        r"control.*spend",
    ],
    "savings_plan": [
        r"savings plan",
        r"saving.*plan",
        r"plan.*save",
        r"investment plan",
        r"financial plan",
        r"budget plan",
        r"plan.*budget",
    ],
    "health_score": [
        r"health.*score",
        r"financial.*health",
        r"score",
        r"my.*score",
        r"how.*(good|bad).*finance",
    ],
    "category_detail": [
        r"food|dining|restaurant|eat",
        r"transport|travel|fuel|cab|uber",
        r"entertain|movie|outing|party",
        r"shopping|clothes|fashion",
        r"rent|house|accommodation",
        r"medical|health|doctor|pharmacy",
        r"study|education|coaching|course",
        r"subscription|netflix|amazon|spotify",
    ],
    "help": [
        r"help",
        r"what can you do",
        r"what.*ask",
        r"commands",
        r"options",
        r"menu",
    ],
}


def detect_intent(user_input: str) -> str:
    text = user_input.lower().strip()

    if any(g in text for g in GREETINGS):
        return "greeting"
    if any(f in text for f in FAREWELLS):
        return "farewell"

    for intent, patterns in INTENT_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text):
                return intent

    return "unknown"


# ─────────────────────────────────────────────────────────────────────────────
# Response Generators (one per intent)
# ─────────────────────────────────────────────────────────────────────────────

def _resp_greeting(df: pd.DataFrame) -> str:
    total = _total_spent(df)
    greets = [
        "Hey! 👋 I'm your PyChamp Finance Advisor. Ready to optimize your money!",
        "Hello! 💰 I'm here to help you take control of your finances.",
        "Hi there! 🚀 Let's make your money work smarter for you.",
    ]
    base = random.choice(greets)
    if total > 0:
        base += f"\n\nQuick snapshot: You've spent **{_format_inr(total)}** in total. Ask me anything!"
    else:
        base += "\n\nI don't see any expenses yet. Start by adding or uploading transactions — then I can give you real insights!"
    return base


def _resp_farewell(_df: pd.DataFrame) -> str:
    return "👋 Take care! Remember — every rupee saved today is wealth tomorrow. Come back anytime!"


def _resp_help(_df: pd.DataFrame) -> str:
    return """**Here's what you can ask me:**

💸 **Spending**
- "How much did I spend?"
- "Show my category breakdown"
- "What's my top spending category?"

📊 **Analysis**
- "Analyze my spending pattern"
- "What are my monthly trends?"

💡 **Advice**
- "How can I save money?"
- "Give me a savings plan"
- "How do I reduce expenses?"
- "What's my financial health score?"

🔍 **Category-specific**
- "How much did I spend on food?"
- "Show my transport expenses"

Just ask naturally — I understand plain English!"""


def _resp_total_spend(df: pd.DataFrame) -> str:
    if df.empty:
        return "📭 No expense data found. Add some transactions first and I'll give you a full spending analysis!"

    total = _total_spent(df)
    top_cat, top_val = _top_category(df)
    pct = (top_val / total * 100) if total > 0 else 0
    savings_pot = _savings_potential(df)
    score = _health_score(df)

    resp = f"💰 **Total Spent: {_format_inr(total)}**\n\n"
    if top_cat:
        resp += f"📌 Your biggest expense is **{top_cat}** at {_format_inr(top_val)} ({pct:.0f}% of total).\n\n"

    if savings_pot > 0:
        resp += f"💡 By cutting non-essential spending by just 20%, you could save **{_format_inr(savings_pot)}** — that's real money!\n\n"

    resp += f"📊 Your Financial Health Score: **{score}/100**"
    if score >= 80:
        resp += " ✅ — Excellent discipline!"
    elif score >= 60:
        resp += " 🔵 — Good, but room to improve."
    elif score >= 40:
        resp += " ⚠️ — Warning: you're nearing budget limits."
    else:
        resp += " 🔴 — Critical: you've exceeded healthy spending levels."
    return resp


def _resp_top_category(df: pd.DataFrame) -> str:
    if df.empty:
        return "📭 No data to analyze. Please add your expenses first."

    breakdown = _category_breakdown(df)
    total = _total_spent(df)
    top_cat, top_val = breakdown.index[0], float(breakdown.iloc[0])
    pct = top_val / total * 100

    resp = f"🏆 **Highest Spending Category: {top_cat}**\n"
    resp += f"- Amount: **{_format_inr(top_val)}** ({pct:.0f}% of total)\n\n"

    resp += "**Full Category Breakdown:**\n"
    for cat, amt in breakdown.items():
        bar_len = int((amt / total) * 20)
        bar = "█" * bar_len + "░" * (20 - bar_len)
        resp += f"- `{bar}` **{cat}**: {_format_inr(amt)} ({amt/total*100:.0f}%)\n"

    is_essential = top_cat.lower() in ESSENTIAL_CATEGORIES
    if not is_essential and pct > 35:
        resp += f"\n⚠️ **Alert:** {top_cat} is a non-essential category taking up {pct:.0f}% of your budget. Try to cap it below 25%."
    elif is_essential:
        resp += f"\n✅ {top_cat} is an essential/investment category — keep it up, but keep it within 40% of your budget."

    return resp


def _resp_savings_advice(df: pd.DataFrame) -> str:
    disc = _discretionary_spend(df)
    total = _total_spent(df)

    if df.empty or total == 0:
        return "📭 Add expense data first and I'll give you personalized savings tips!"

    tip = random.choice(SAVINGS_TIPS)
    savings_pot = float(disc.sum() * 0.20)

    resp = f"💡 **Personalized Savings Strategy:**\n\n"

    if not disc.empty:
        top_waste = disc.index[0]
        top_waste_amt = float(disc.iloc[0])
        resp += f"**🔴 Cut First:** Reduce **{top_waste}** spending by 20% → Save **{_format_inr(top_waste_amt * 0.2)}/month**\n\n"

    if savings_pot > 0:
        resp += f"**💰 Total Savings Potential:** {_format_inr(savings_pot)}/month by trimming non-essential spend by 20%.\n\n"

    monthly_target = total * 0.20
    resp += f"**🎯 Savings Goal:** Aim to save **{_format_inr(monthly_target)}/month** (20% of spending).\n\n"
    resp += f"**💎 Pro Tip:** {tip}"

    return resp


def _resp_spending_pattern(df: pd.DataFrame) -> str:
    if df.empty:
        return "📭 No data available. Start tracking expenses to uncover your spending patterns!"

    monthly = _monthly_breakdown(df)
    total = _total_spent(df)
    disc = _discretionary_spend(df)
    disc_total = float(disc.sum())
    essential_total = total - disc_total

    resp = "📊 **Spending Pattern Analysis**\n\n"

    if not monthly.empty:
        resp += "**Monthly Trend:**\n"
        for _, row in monthly.iterrows():
            resp += f"- {row['month']}: **{_format_inr(row['total'])}**\n"
        resp += "\n"

    resp += f"**Essential vs Discretionary:**\n"
    resp += f"- 🟢 Essential (rent, education, health): **{_format_inr(essential_total)}** ({essential_total/total*100:.0f}%)\n"
    resp += f"- 🔴 Discretionary (lifestyle, entertainment): **{_format_inr(disc_total)}** ({disc_total/total*100:.0f}%)\n\n"

    if disc_total / total > 0.5:
        resp += "⚠️ **Pattern Alert:** More than 50% of your spending is on non-essentials. This is a red flag — you should rebalance immediately."
    elif disc_total / total > 0.3:
        resp += "🔵 **Moderate Concern:** Non-essential spending is between 30–50%. Try to push it below 30%."
    else:
        resp += "✅ **Healthy Pattern:** Your discretionary spending is under control. Keep consistent!"

    return resp


def _resp_reduce_expense(df: pd.DataFrame) -> str:
    if df.empty:
        return "📭 Add your expense data first so I can give you targeted cost-cutting advice."

    disc = _discretionary_spend(df)
    total = _total_spent(df)

    resp = "✂️ **Expense Reduction Plan:**\n\n"

    if disc.empty:
        return "✅ All your expenses are essential — nothing to cut! You're spending very wisely."

    for i, (cat, amt) in enumerate(disc.items()):
        if i >= 4:
            break
        cut = amt * 0.20
        resp += f"**{i+1}. {cat}** — Spend {_format_inr(amt)} → Cut 20% → Save **{_format_inr(cut)}/month**\n"

    total_cut = float(disc.sum() * 0.20)
    resp += f"\n💰 **Total Savings if all cuts applied: {_format_inr(total_cut)}/month**\n\n"
    resp += "📌 **Action Steps:**\n"
    resp += "1. Set a weekly spending cap for each non-essential category.\n"
    resp += "2. Review subscriptions — cancel unused ones immediately.\n"
    resp += "3. For food/dining — cook at home 4 days a week.\n"
    resp += "4. Zero-in on your top 2 wastage categories and track them daily."

    return resp


def _resp_savings_plan(df: pd.DataFrame) -> str:
    total = _total_spent(df)

    if total == 0:
        return "📭 I need your expense data to build a personalized savings plan. Add transactions first!"

    monthly_income_estimate = total / 0.7  # Assume spending is ~70% of income
    savings_20 = monthly_income_estimate * 0.20
    savings_aggressive = monthly_income_estimate * 0.30

    resp = "📋 **Your Personalized Savings Plan:**\n\n"
    resp += f"Based on your spending of **{_format_inr(total)}**, here's a structured plan:\n\n"

    resp += "**🎯 Monthly Targets:**\n"
    resp += f"- Conservative (20% savings): **{_format_inr(savings_20)}/month**\n"
    resp += f"- Aggressive (30% savings): **{_format_inr(savings_aggressive)}/month**\n\n"

    resp += "**📅 6-Month Roadmap:**\n"
    resp += f"- Month 1–2: Identify and eliminate top 2 wastage areas. Target: save {_format_inr(savings_20 * 2)}.\n"
    resp += f"- Month 3–4: Automate savings. Set up SIP of ₹{savings_20 * 0.5:,.0f}/month in a liquid fund.\n"
    resp += f"- Month 5–6: Build emergency fund of **{_format_inr(savings_20 * 3)}** (3 months of expenses).\n\n"

    resp += "**💡 Recommended Allocation:**\n"
    resp += f"- Emergency Fund: 30% of savings → {_format_inr(savings_20 * 0.3)}/month\n"
    resp += f"- Investments (SIP/Index Funds): 50% → {_format_inr(savings_20 * 0.5)}/month\n"
    resp += f"- Personal Goals: 20% → {_format_inr(savings_20 * 0.2)}/month\n"

    return resp


def _resp_health_score(df: pd.DataFrame) -> str:
    if df.empty:
        return "📭 No expense data found. Add transactions to calculate your Financial Health Score."

    score = _health_score(df)
    total = _total_spent(df)

    if score >= 80:
        status, icon = "Excellent", "🟢"
        advice = "You're managing money like a pro. Keep it up and focus on building investments!"
    elif score >= 60:
        status, icon = "Good", "🔵"
        advice = "Solid foundation! Small reductions in discretionary spend will push you to Excellent."
    elif score >= 40:
        status, icon = "Warning", "🟡"
        advice = "You're nearing your budget limits. Cut non-essential expenses this week to recover."
    else:
        status, icon = "Critical", "🔴"
        advice = "You've crossed your safe spending threshold. Immediate action required — stop all non-essential spending now!"

    resp = f"{icon} **Financial Health Score: {score}/100 — {status}**\n\n"
    resp += f"💰 Total Spending Analyzed: **{_format_inr(total)}**\n\n"
    resp += f"💬 **Advisor's Take:** {advice}\n\n"
    resp += "**Score Guide:**\n"
    resp += "- 80–100: 🟢 Excellent | 60–79: 🔵 Good | 40–59: 🟡 Warning | 0–39: 🔴 Critical"

    return resp


def _resp_category_detail(user_input: str, df: pd.DataFrame) -> str:
    if df.empty:
        return "📭 No expense data found."

    # Extract which category the user asked about
    cat_keywords = {
        "food": ["food", "dining", "restaurant", "eat", "meal"],
        "transport": ["transport", "travel", "fuel", "cab", "uber", "ola"],
        "entertainment": ["entertain", "movie", "outing", "party", "fun"],
        "shopping": ["shopping", "clothes", "fashion"],
        "rent": ["rent", "house", "accommodation"],
        "medical": ["medical", "health", "doctor", "pharmacy"],
        "study": ["study", "education", "coaching", "course", "tuition"],
        "subscriptions": ["subscription", "netflix", "amazon", "spotify"],
    }

    text = user_input.lower()
    matched_group = None
    matched_keywords = []
    for group, words in cat_keywords.items():
        for w in words:
            if w in text:
                matched_group = group
                matched_keywords = words
                break
        if matched_group:
            break

    if not matched_group:
        return _resp_top_category(df)

    # Find matching rows
    mask = df["category"].str.lower().apply(
        lambda c: any(w in c for w in matched_keywords)
    )
    filtered = df[mask]

    if filtered.empty:
        return f"🔍 No **{matched_group}** expenses found in your records. Either you haven't added any, or they may be categorized differently."

    amt = float(filtered["amount"].sum())
    total = _total_spent(df)
    pct = amt / total * 100

    resp = f"🔍 **{matched_group.title()} Spending:** {_format_inr(amt)} ({pct:.0f}% of total)\n\n"

    is_essential = matched_group in {"rent", "medical", "study"}
    if not is_essential and pct > 25:
        recommended_cut = amt * 0.20
        resp += f"⚠️ That's a significant chunk. To optimize, try reducing **{matched_group}** spend by 20% → Save **{_format_inr(recommended_cut)}/month**."
    elif is_essential:
        resp += f"✅ **{matched_group.title()}** is an essential category. Spending here is justified — just make sure it doesn't dominate your budget (keep it below 40% of total)."
    else:
        resp += f"✅ Your **{matched_group}** spending looks reasonable at {pct:.0f}% of total."

    return resp


def _resp_unknown(_df: pd.DataFrame) -> str:
    suggestions = [
        "How much did I spend this month?",
        "What's my top spending category?",
        "Give me a savings plan",
        "How can I reduce my expenses?",
        "What's my financial health score?",
    ]
    tip = random.choice(suggestions)
    return f"🤔 I didn't quite catch that. I specialize in **financial analysis** — try asking things like:\n\n> *\"{tip}\"*\n\nOr type **help** to see everything I can do."


# ─────────────────────────────────────────────────────────────────────────────
# Master Dispatcher
# ─────────────────────────────────────────────────────────────────────────────

INTENT_HANDLERS = {
    "greeting": _resp_greeting,
    "farewell": _resp_farewell,
    "help": _resp_help,
    "total_spend": _resp_total_spend,
    "top_category": _resp_top_category,
    "savings_advice": _resp_savings_advice,
    "spending_pattern": _resp_spending_pattern,
    "reduce_expense": _resp_reduce_expense,
    "savings_plan": _resp_savings_plan,
    "health_score": _resp_health_score,
    "unknown": _resp_unknown,
}


def get_chatbot_response(user_input: str, df: pd.DataFrame) -> str:
    """
    Main entry point for the PyChamp AI Finance Chatbot.

    Args:
        user_input : str — The user's raw message.
        df         : pd.DataFrame — Expenses DataFrame with columns:
                     [date, category, amount, note]

    Returns:
        str — Formatted markdown response from the financial advisor bot.
    """
    if not user_input or not user_input.strip():
        return "Please type a question and I'll analyze your finances! 💬"

    intent = detect_intent(user_input)

    # Category detail intent needs the raw input to pick the right category
    if intent == "category_detail":
        return _resp_category_detail(user_input, df)

    handler = INTENT_HANDLERS.get(intent, _resp_unknown)
    return handler(df)
