import streamlit as st
import menu_page
from sqlalchemy import create_engine, text

DB_URL = "postgresql+pg8000://andhiyaulhaq:mysecretpassword@localhost:5435/ks_test"
engine = create_engine(DB_URL)


def main():
    st.set_page_config(page_title="APPS", page_icon=":key:")
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        login_page()
    else:
        menu_page.main()


def get_role(username):
    with engine.connect() as conn:
        query = text("SELECT role FROM user_admin WHERE username = :username")
        result = conn.execute(query, {"username": username}).fetchone()
    return result


def login_page():
    st.title("Login Page")
    st.subheader("Welcome! Please login to continue.")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "":
            st.write("Please fill username")
        elif password != "" and len(password) < 8:
            st.write("Please fill correct password")
        if authenticate(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username
            role_get = get_role(username)
            st.session_state.role = role_get[0]
            with engine.connect() as conn:
                query = text(
                    "select id_user from user_admin where username = :username"
                )
                result = conn.execute(query, {"username": username}).fetchone()
            id_user = result[0]
            st.session_state.id_user = id_user
            with engine.connect() as conn:
                query = text(
                    (
                        """
                        INSERT INTO operation (start_time, id_user) 
                        VALUES (NOW(), :id_user)
                    """
                    )
                )
                conn.execute(query, {"id_user": id_user})
                conn.commit()
            st.rerun()
        else:
            st.error("Invalid username or password. Please try again.")


def authenticate(username, password):
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


if __name__ == "__main__":
    main()
