import streamlit as st

import src.admin.app as admin
import src.auth as auth  # Import authentication module
import src.detect.app as detect
import src.label.app as label
import src.welcome.app as welcome


def main():
    """Main function for handling menu navigation after login."""
    if not st.session_state.get("logged_in", False):
        st.warning("Please log in first.")
        return

    menu_option = st.sidebar.selectbox(
        "Select Menu", ("Welcome Page", "Detect", "Label", "Admin Page")
    )

    menu_navigation(menu_option)

    if st.sidebar.button("Logout"):
        auth.logout()  # Use logout function from auth.py


def menu_navigation(menu_option):
    """Navigate to the appropriate page."""
    if menu_option == "Welcome Page":
        welcome.main()
    elif menu_option == "Detect":
        detect.main()
    elif menu_option == "Label":
        label.main()
    elif menu_option == "Admin Page":
        admin.main()
