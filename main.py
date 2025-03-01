"""
Main streamlit module.
"""

import streamlit as st

import src.menu_page as menu_page
from src.login.ui import render_login_ui

st.set_page_config(page_title="APPS", page_icon=":key:")


def main():
    """Initialize the Streamlit app and handle authentication."""
    if not st.session_state.get("logged_in", False):
        render_login_ui()
    else:
        menu_page.main()


if __name__ == "__main__":
    main()
