import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import logging
from typing import Optional, Dict, Any

import streamlit as st
from auth import login_user, register_user
from database import init_db, load_expenses
from utils.finance_rules import calculate_health_score, get_health_status

from page_views.overview import render_overview
from page_views.expenses import render_expenses
from page_views.upload import render_upload
from page_views.ai_insights import render_insights
from page_views.chatbot import render_chatbot
from page_views.predictions import render_predictions

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="PyChamp | AI Finance Analyzer",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Injected first — scroll fix + hide Streamlit loader ─────────────────────
st.markdown("""
<style>
/* ── SCROLL FIX ─────────────────────────────────────────────────────── */
html, body {
    overflow: auto !important;
    height: auto !important;
    min-height: 100vh !important;
}
.stApp {
    overflow-y: auto !important;
    overflow-x: hidden !important;
    height: auto !important;
    min-height: 100vh !important;
}
[data-testid="stAppViewContainer"] {
    overflow-y: auto !important;
    overflow-x: hidden !important;
    height: auto !important;
    min-height: 100vh !important;
}
[data-testid="stMain"] {
    overflow-y: auto !important;
    height: auto !important;
}
[data-testid="block-container"],
.block-container,
.main .block-container {
    overflow-y: auto !important;
    max-height: none !important;
    height: auto !important;
    padding-bottom: 5rem !important;
}

/* ── HIDE STREAMLIT LOADER & STATUS ────────────────────────────────── */
/* Running indicator top-right */
[data-testid="stStatusWidget"]      { display: none !important; visibility: hidden !important; }

/* Skeleton loading grey boxes */
[data-testid="stSkeleton"]          { display: none !important; }
div[class*="skeleton"]              { display: none !important; }
div[class*="Skeleton"]              { display: none !important; }

/* Top linear progress loader bar */
[data-testid="stSpinner"]           { display: none !important; }
.stSpinner                          { display: none !important; }

/* Prevent grey fade during rerun */
[data-stale="true"]                 { opacity: 1 !important; transition: none !important; }
.stApp[data-stale="true"]           { opacity: 1 !important; }

/* Footer & menu */
footer                              { display: none !important; }
#MainMenu                           { display: none !important; }
[data-testid="stDecoration"]        { display: none !important; }
[data-testid="stToolbar"]           { display: none !important; }
</style>
""", unsafe_allow_html=True)

def local_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except Exception:
        pass

local_css("assets/style.css")


def initialize_session() -> None:
    try:
        if "db_initialized" not in st.session_state:
            init_db()
            st.session_state.db_initialized = True
        if "logged_in" not in st.session_state:
            st.session_state.logged_in = False
        if "user" not in st.session_state:
            st.session_state.user = {}
        if "current_page" not in st.session_state:
            st.session_state.current_page = "Overview"
    except Exception as e:
        st.error("Critical error starting application.")


def render_login_page() -> None:
    st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none !important; }
    .block-container { padding-top: 6rem !important; max-width: 1100px !important; }
    </style>
    """, unsafe_allow_html=True)

    col1, gap, col2 = st.columns([1.3, 0.15, 0.95])

    with col1:
        st.markdown("""
        <div style="animation: fadeInUp 0.7s ease both;">
            <div style="display:flex; align-items:center; gap:10px; margin-bottom:1.5rem;">
                <span style="font-size:2rem;">⚡</span>
                <span style="font-size:1rem; font-weight:700; color:#475569; letter-spacing:0.15em; text-transform:uppercase; font-family:'Inter',sans-serif;">PyChamp</span>
            </div>
            <div class="hero-title">Master Your<br/>Finances with AI.</div>
            <div class="hero-subtitle">
                Your personalized wealth engine. Track daily expenses, discover hidden spending patterns,
                and leverage enterprise-grade ML forecasts to optimize your financial future.
            </div>
            <div style="display:flex; gap:1rem; flex-wrap:wrap; margin-top:0.5rem;">
                <div class="stat-badge">
                    <div class="stat-badge-val">98%</div>
                    <div class="stat-badge-lbl">Budget Accuracy</div>
                </div>
                <div class="stat-badge">
                    <div class="stat-badge-val">Real-time</div>
                    <div class="stat-badge-lbl">ML Forecasting</div>
                </div>
                <div class="stat-badge">
                    <div class="stat-badge-val">AI-First</div>
                    <div class="stat-badge-lbl">Insights Engine</div>
                </div>
            </div>
        </div>
        <style>
        @keyframes fadeInUp {
            from { opacity:0; transform:translateY(24px); }
            to   { opacity:1; transform:translateY(0); }
        }
        </style>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="login-card">
        <div style="margin-bottom:1.5rem;">
            <div style="font-size:1.2rem; font-weight:800; color:#f8fafc; font-family:'Outfit',sans-serif; margin-bottom:4px;">Welcome back</div>
            <div style="font-size:0.82rem; color:#475569; font-family:'Inter',sans-serif;">Sign in to your financial dashboard</div>
        </div>
        </div>
        """, unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["🔐 Sign In", "✨ Create Account"])

        with tab1:
            username = st.text_input("Username", key="login_user", placeholder="Enter your username")
            password = st.text_input("Password", type="password", key="login_pass", placeholder="••••••••")
            st.write("")
            if st.button("Sign In →", use_container_width=True, type="primary", key="signin_btn"):
                handle_login(username, password)

        with tab2:
            new_user = st.text_input("Username *", key="reg_user", placeholder="Choose a username")
            new_email = st.text_input("Email Address", key="reg_email", placeholder="you@example.com")
            new_phone = st.text_input("Phone Number", key="reg_phone", placeholder="+91 98765 43210")
            new_pass = st.text_input("Password *", type="password", key="reg_pass", placeholder="Min. 6 characters")
            confirm_pass = st.text_input("Confirm Password *", type="password", key="reg_confirm", placeholder="Re-enter password")
            st.write("")
            if st.button("Create Account →", use_container_width=True, type="primary", key="register_btn"):
                handle_registration(new_user, new_pass, confirm_pass, new_email, new_phone)




def handle_login(username, password):
    if not username or not password:
        st.error("Please provide both username and password.")
        return
    user = login_user(username, password)
    if user:
        st.session_state.logged_in = True
        st.session_state.user = user
        st.rerun()
    else:
        st.error("❌ Invalid credentials. Please try again.")


def handle_registration(username, password, confirm_pass, email, phone):
    if not username or not password or not confirm_pass:
        st.error("Please fill out required fields *.")
        return
    if password != confirm_pass:
        st.error("Passwords do not match.")
        return
    if len(password) < 6:
        st.warning("Password must be at least 6 characters.")
        return
    if register_user(username, password, email, phone):
        st.session_state.logged_in = True
        st.session_state.user = login_user(username, password)
        st.rerun()
    else:
        st.error("Registration failed. Username already taken.")


# ─── NAV ITEMS ─────────────────────────────────────────────────────────────
NAV_MAIN = [
    ("🏠", "Overview"),
    ("💳", "Expenses"),
    ("📤", "Import CSV"),
]
NAV_ANALYTICS = [
    ("✨", "AI Insights"),
    ("💬", "AI Chatbot"),
    ("📈", "ML Predictions"),
]


def render_sidebar(user: Dict[str, Any]) -> None:
    with st.sidebar:
        # Brand
        st.markdown("""
        <div style="display:flex; align-items:center; gap:10px; padding:0.25rem 0 1.25rem 0;">
            <span style="font-size:1.6rem;">⚡</span>
            <div>
                <div style="font-size:1.05rem; font-weight:800; color:#f8fafc; font-family:'Outfit',sans-serif; letter-spacing:-0.02em;">PYCHAMP</div>
                <div style="font-size:0.68rem; color:#334155; font-family:'Inter',sans-serif; letter-spacing:0.1em; text-transform:uppercase; font-weight:600;">AI Finance Analyzer</div>
            </div>
        </div>
        <div class="sidebar-divider"></div>
        """, unsafe_allow_html=True)

        # Main nav
        st.markdown('<div class="sidebar-section-label">Main</div>', unsafe_allow_html=True)
        for icon, name in NAV_MAIN:
            is_active = st.session_state.current_page == name
            btn_style = (
                "background:rgba(0,229,153,0.08) !important; color:#00e599 !important; "
                "border-left:3px solid #00e599 !important; font-weight:600 !important;"
            ) if is_active else ""
            if is_active:
                st.markdown(f"""
                <style>
                div[data-testid="stSidebar"] div[data-testid="element-container"]:has(button[key="nav_{name}"]) button {{
                    background: rgba(0,229,153,0.08) !important;
                    color: #00e599 !important;
                    border-left: 3px solid #00e599 !important;
                    font-weight: 600 !important;
                }}
                </style>""", unsafe_allow_html=True)
            if st.button(f"{icon}  {name}", key=f"nav_{name}", use_container_width=True):
                st.session_state.current_page = name
                st.rerun()

        st.markdown('<div class="sidebar-divider" style="margin:0.75rem 0;"></div>', unsafe_allow_html=True)

        # Analytics nav
        st.markdown('<div class="sidebar-section-label">Analytics</div>', unsafe_allow_html=True)
        for icon, name in NAV_ANALYTICS:
            if st.button(f"{icon}  {name}", key=f"nav_{name}", use_container_width=True):
                st.session_state.current_page = name
                st.rerun()

        st.markdown('<div class="sidebar-divider" style="margin:1rem 0; opacity:0;"></div>', unsafe_allow_html=True)

        # Health score
        df = load_expenses(user.get("username"))
        total = df['amount'].sum() if not df.empty else 0
        score = calculate_health_score(total)
        status_text, status_col = get_health_status(score)

        st.markdown(f"""
        <div class="health-box">
            <div class="health-title">Financial Health</div>
            <div class="health-score">{score}<span style="font-size:1rem; color:#334155; font-weight:500;">/100</span></div>
            <div class="health-sub">{status_text}</div>
            <div class="health-progress">
                <div class="health-bar" style="width:{score}%; background:{status_col};"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # User badge
        username = user.get('username', 'User')
        role = user.get("role") or "User"
        initials = username[:2].upper()

        st.markdown(f"""
        <div class="user-badge">
            <div class="avatar">{initials}</div>
            <div class="user-info">
                <span class="user-name">{username.capitalize()}</span>
                <span class="user-role">{role.capitalize()} • <span style="color:#00e599;">Premium</span></span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.write("")
        if st.button("⎋  Sign Out", key="logout_btn", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user = {}
            st.rerun()


def main() -> None:
    initialize_session()

    if st.session_state.logged_in:
        user = st.session_state.user
        render_sidebar(user)

        page = st.session_state.current_page
        if page == "Overview":
            render_overview(user.get("username"))
        elif page == "Expenses":
            render_expenses(user.get("username"))
        elif page == "Import CSV":
            render_upload(user.get("username"))
        elif page == "AI Insights":
            render_insights(user.get("username"))
        elif page == "AI Chatbot":
            render_chatbot(user.get("username"))
        elif page == "ML Predictions":
            render_predictions(user.get("username"))
    else:
        render_login_page()


if __name__ == "__main__":
    main()