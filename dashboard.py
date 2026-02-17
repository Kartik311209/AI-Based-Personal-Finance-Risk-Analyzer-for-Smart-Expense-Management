import streamlit as st
from finance_analyzer import finance_app


def show_dashboard(username, role):
    st.title("🤖 PyChamp Ultra AI Dashboard")
    st.success(f"Welcome {username} ({role}) 🚀")

    menu = st.sidebar.radio(
        "📌 PyChamp Menu",
        ["🏠 Home", "📊 Finance Analyzer", "🤖 AI Chatbot", "🚪 Logout"]
    )

    if menu == "🏠 Home":
        st.write("🔥 PyChamp is now integrated with Finance AI!")

    elif menu == "📊 Finance Analyzer":
        finance_app()

    elif menu == "🤖 AI Chatbot":
        st.write("🤖 PyChamp Chatbot Coming Soon...")

    elif menu == "🚪 Logout":
        st.session_state.logged_in = False
        st.session_state.user = None   # ⭐ important
        st.rerun()
