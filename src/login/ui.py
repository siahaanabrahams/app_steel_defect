"""
Login UI module.
"""

import streamlit as st

from .handler import handle_login


def render_login_ui():
    """Render the login UI."""
    st.title("Login Page")
    st.subheader("Welcome! Please login to continue")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        handle_login(username, password)
