# ⚡ PyChamp AI Finance Analyzer

> **An intelligent, AI-powered personal finance management platform built with Python & Streamlit.**

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.x-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## 📌 Overview

PyChamp AI Finance Analyzer is a full-stack, AI-powered personal finance dashboard designed to help users track expenses, discover spending patterns, and leverage machine learning forecasts to optimize their financial health. It features a modern, dark-themed glassmorphism UI, secure multi-user authentication, and a suite of analytical tools — all running locally with zero cloud dependency.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔐 **Secure Authentication** | Register/login with hashed password storage using SQLite |
| 🏠 **Financial Overview** | Real-time KPI cards showing total spend, categories & health score |
| 💳 **Expense Tracker** | Add, edit, and delete expenses with category tagging |
| 📤 **CSV Import** | Bulk import transaction history via CSV upload |
| ✨ **AI Insights** | Rule-based financial health analysis & personalized recommendations |
| 💬 **AI Chatbot** | Conversational finance assistant powered by Google Gemini |
| 📈 **ML Predictions** | Machine learning-based spend forecasting using historical data |
| 💯 **Health Score** | Dynamic financial health score (0–100) shown in the sidebar |

---

## 🗂️ Project Structure

```
Finance-Analyzer/
│
├── app.py                  # Main Streamlit entry point & routing
├── auth.py                 # User registration & login logic
├── database.py             # SQLite DB initialization & expense queries
│
├── page_views/             # Individual page renderers
│   ├── overview.py         # Dashboard overview page
│   ├── expenses.py         # Expense management page
│   ├── upload.py           # CSV import page
│   ├── ai_insights.py      # AI-generated insights page
│   ├── chatbot.py          # AI chatbot interface
│   └── predictions.py      # ML forecasting page
│
├── utils/                  # Shared utility modules
│   ├── chatbot.py          # Gemini API integration logic
│   ├── charts.py           # Plotly chart builders
│   ├── finance_rules.py    # Health score & financial rules engine
│   └── ml_model.py         # ML model training & prediction
│
├── assets/
│   └── style.css           # Global custom CSS (glassmorphism theme)
│
├── data/                   # Local data storage
├── expenses.db             # SQLite database for expenses
├── users.db                # SQLite database for user accounts
└── .streamlit/             # Streamlit configuration
```

---

## 🚀 Getting Started

### Prerequisites

- Python **3.9+**
- pip

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/Finance-Analyzer.git
cd Finance-Analyzer
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

> **Core dependencies:** `streamlit`, `pandas`, `plotly`, `scikit-learn`, `google-generativeai`, `bcrypt`

If you don't have a `requirements.txt` yet, install manually:

```bash
pip install streamlit pandas plotly scikit-learn google-generativeai bcrypt
```

### 3. Configure the AI Chatbot *(Optional)*

To enable the AI Chatbot feature, set your **Google Gemini API key**:

```bash
# Windows PowerShell
$env:GOOGLE_API_KEY = "your_api_key_here"

# Or add it to a .env file
GOOGLE_API_KEY=your_api_key_here
```

### 4. Run the App

```bash
streamlit run app.py
```

The app will open at **http://localhost:8501**

---

## 🖥️ Usage

1. **Register** a new account or **Sign In** with existing credentials.
2. Navigate using the **sidebar**:
   - **Overview** — See your spending summary and financial health score.
   - **Expenses** — Add or manage individual expense entries.
   - **Import CSV** — Bulk-upload transactions from a `.csv` file.
   - **AI Insights** — Get rule-based financial recommendations.
   - **AI Chatbot** — Chat with your personal finance AI advisor.
   - **ML Predictions** — View ML-powered forecasts for upcoming months.

### CSV Import Format

Your CSV file should include the following columns:

```
date, category, description, amount
2024-01-15, Food, Lunch at Cafe, 250.00
2024-01-16, Transport, Uber ride, 85.00
```

---

## 🤖 AI & ML Capabilities

### Google Gemini Chatbot
- Analyzes your personal expense DataFrame
- Provides actionable financial advice and savings plans
- Identifies top spending categories and patterns
- Maintains a smart financial advisor persona

### ML Forecasting
- Trains on your historical expense data
- Predicts future monthly spending using regression models (scikit-learn)
- Supports per-category trend analysis

### Financial Health Score
- Dynamically calculated based on total monthly spending
- Color-coded status: 🟢 Excellent → 🔴 Critical
- Displayed live in the sidebar

---

## 🎨 Design System

- **Theme:** Dark glassmorphism with neon green accents (`#00e599`)
- **Fonts:** Inter, Outfit (Google Fonts)
- **Charts:** Plotly interactive visualizations
- **Animations:** CSS fade-in / slide-up micro-animations

---

## 🔒 Security

- Passwords are hashed before storage (never stored in plain text)
- Per-user data isolation — each user only sees their own expenses
- SQLite databases stored locally; no external data transmission

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Kartik** — BTech Final Year Project  
*PyChamp AI Finance Analyzer | 2026*

---

> *"Master your finances with AI."* ⚡
