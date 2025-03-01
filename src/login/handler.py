"""
Login handler module.
"""

import streamlit as st

from src.auth import authenticate, get_role, get_user_id, log_user_session


def handle_login(username, password):
    """Handle user authentication and session management."""
    if not username:
        st.write("Please fill in the username")
        return
    if password and len(password) < 8:
        st.write("Please enter a valid password")
        return

    if authenticate(username, password):
        st.session_state.logged_in = True
        st.session_state.username = username

        role = get_role(username)
        if role:
            st.session_state.role = role

        user_id = get_user_id(username)
        if user_id:
            st.session_state.id_user = user_id
            log_user_session(user_id)

        st.rerun()
    else:
        st.error("Invalid username or password. Please try again.")
