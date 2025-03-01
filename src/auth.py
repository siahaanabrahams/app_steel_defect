"""Authentication and authorization functions."""

import streamlit as st
from sqlalchemy import create_engine, text

# Database Configuration
DB_URL = "postgresql+pg8000://andhiyaulhaq:mysecretpassword@localhost:5435/ks_test"
engine = create_engine(DB_URL)


def get_role(username):
    """Retrieve the user role from the database."""
    with engine.connect() as conn:
        query = text("SELECT role FROM user_admin WHERE username = :username")
        result = conn.execute(query, {"username": username}).fetchone()
    return result[0] if result else None


def get_user_id(username):
    """Retrieve the user ID for a given username."""
    with engine.connect() as conn:
        query = text("SELECT id_user FROM user_admin WHERE username = :username")
        result = conn.execute(query, {"username": username}).fetchone()
    return result[0] if result else None


def log_user_session(user_id):
    """Log the start of a user's session in the operation table."""
    with engine.connect() as conn:
        query = text(
            "INSERT INTO operation (start_time, id_user) VALUES (NOW(), :id_user)"
        )
        conn.execute(query, {"id_user": user_id})
        conn.commit()


def authenticate(username, password):
    """Authenticate the user against the database."""
    try:
        with engine.connect() as conn:
            query = text(
                "SELECT * FROM user_admin WHERE username = :username AND password = :password"
            )
            result = conn.execute(
                query, {"username": username, "password": password}
            ).fetchone()
            return result is not None
    except Exception as e:
        st.error(f"Database error: {e}")
        return False


def get_last_operation_id(user_id):
    """Retrieve the latest operation ID for a given user."""
    with engine.connect() as conn:
        query = text(
            """
            SELECT id_operation 
            FROM operation 
            WHERE id_user = :id 
            ORDER BY start_time DESC 
            LIMIT 1
            """
        )
        result = conn.execute(query, {"id": user_id}).fetchone()
    return result[0] if result else None


def update_operation_end_time(operation_id):
    """Update the end time of a given operation in the database."""
    if not operation_id:
        return

    with engine.connect() as conn:
        query = text(
            "UPDATE operation SET end_time = NOW() WHERE id_operation = :id_operation"
        )
        conn.execute(query, {"id_operation": operation_id})
        conn.commit()


def clear_session():
    """Clear the Streamlit session state and refresh the UI."""
    st.session_state.clear()
    st.rerun()


def logout():
    """Handle user logout by updating the operation table and clearing session state."""
    user_id = st.session_state.get("id_user")
    if not user_id:
        return

    operation_id = get_last_operation_id(user_id)
    update_operation_end_time(operation_id)
    clear_session()
