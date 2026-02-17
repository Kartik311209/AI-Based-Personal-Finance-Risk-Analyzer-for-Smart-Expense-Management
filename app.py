import streamlit as st
from auth import login_user, register_user
from dashboard import show_dashboard
from database import init_db

st.set_page_config(page_title="PyChamp", layout="wide")

# Initialize database
init_db()

# ---------------- LOGIN PAGE ---------------- #
def login_page():
    st.title("🔐 Dashboard Login")

    tab1, tab2 = st.tabs(["Login", "Register"])

    # -------- LOGIN TAB -------- #
    with tab1:
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")

        if st.button("Login"):
            user = login_user(username, password)

            if user:
                st.session_state.logged_in = True
                st.session_state.user = user
                st.success("Login successful ✅")
                st.rerun()
            else:
                st.error("Invalid credentials ❌")

    # -------- REGISTER TAB -------- #
    with tab2:
        new_user = st.text_input("New Username", key="reg_user")
        new_pass = st.text_input("New Password", type="password", key="reg_pass")

        if st.button("Register"):
            if register_user(new_user, new_pass):
                st.success("Registered successfully 🎉 Please login.")
            else:
                st.error("User already exists ❌")


# ---------------- MAIN APP ---------------- #
def main():

    # Session defaults
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if "user" not in st.session_state:
        st.session_state.user = {}

    # Routing
    if st.session_state.logged_in:
        user = st.session_state.user

        show_dashboard(
            user.get("username", "User"),
            user.get("role", "Guest")
        )
    else:
        login_page()


# ---------------- RUN ---------------- #
if __name__ == "__main__":
    main()
