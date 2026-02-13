import streamlit as st
from auth import login_user, register_user
from dashboard import show_dashboard
from database import init_db

st.set_page_config(page_title="PyChamp", layout="wide")

init_db()

def login_page():
    st.title("🔐 Dashboard Login")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            user = login_user(username, password)
            if user:
                st.session_state["logged_in"] = True
                st.session_state["user"] = user
                st.success("Login successful")
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        new_user = st.text_input("New Username")
        new_pass = st.text_input("New Password", type="password")

        if st.button("Register"):
            if register_user(new_user, new_pass):
                st.success("Registered successfully. Login now.")
            else:
                st.error("User already exists")


def main():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if st.session_state["logged_in"]:
        user = st.session_state["user"]
        show_dashboard(user["username"], user["role"])
    else:
        login_page()


if __name__ == "__main__":
    main()