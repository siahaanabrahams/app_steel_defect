import streamlit as st
from sqlalchemy import create_engine, text
import pandas as pd

DB_URL = "postgresql+pg8000://postgres:abraham@localhost:5432/postgres"
engine = create_engine(DB_URL)

def create_user():
    st.subheader("Create User")
    
    role_new = st.selectbox("Role", ("admin", "user"))
    user_new = st.text_input("Username:")
    pass_new = st.text_input("Password:", type="password")
    
    if st.button("Create"):
        # Validasi input
        if not role_new:
            st.warning("Please select a role.")
        elif not user_new:
            st.warning("Please enter a username.")
        elif not pass_new:
            st.warning("Please enter a password.")
        elif len(pass_new) < 8:
            st.warning("Password must be at least 8 characters long.")
        else:
            with engine.connect() as conn:
                # Periksa apakah username sudah ada
                check_query = text("SELECT COUNT(*) FROM user_admin WHERE username = :username")
                if conn.execute(check_query, {"username": user_new}).scalar() > 0:
                    st.error(f'Error: Username "{user_new}" already exists. Please choose a different username.')
                else:
                    # Tambahkan pengguna baru
                    insert_query = text("""
                        INSERT INTO user_admin (username, password, role) 
                        VALUES (:username, :password, :role)
                    """)
                    conn.execute(insert_query, {"username": user_new, "password": pass_new, "role": role_new})
                    conn.commit()
                    st.success(f'User "{user_new}" has been created successfully.')

def delete_user():
    st.subheader("Delete User")
    
    with engine.connect() as conn:
        query = text("SELECT user_id, username, role FROM user_admin WHERE role != 'admin'")
        result = conn.execute(query).fetchall()
    
    if result:
        result_df = pd.DataFrame(result, columns=['id', 'username', 'role'])
        st.table(result_df)
        
        selected = st.selectbox("Select User", result_df['username'])
        
        if st.button('Delete User'):
            try:
                with engine.connect() as conn:
                    delete_query = text("DELETE FROM user_admin WHERE username = :username")
                    conn.execute(delete_query, {"username": selected})
                    conn.commit()
                
                st.success(f'User "{selected}" has been deleted.')
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Database error: {e}")
    else:
        st.write('No user detected.')

def change_password():
    st.subheader("Change Password")
    
    pass_lama = st.text_input("Old Password", type="password")
    pass_baru = st.text_input("New Password", type="password")
    pass_baru_konf = st.text_input("Confirm New Password", type="password")
    
    if st.button('Confirm'):
        # Validasi input
        if not pass_lama:
            st.warning("Please fill in your old password.")
        elif not pass_baru:
            st.warning("Please fill in your new password.")
        elif len(pass_baru) < 8:
            st.warning("New password must be at least 8 characters.")
        elif not pass_baru_konf:
            st.warning("Please fill in the new password confirmation.")
        elif pass_baru == pass_lama:
            st.warning("New password cannot be the same as the old password.")
        elif pass_baru != pass_baru_konf:
            st.warning("New password confirmation does not match the new password.")
        else:
            # Verifikasi old password dan update password
            with engine.connect() as conn:
                query = text("SELECT password FROM user_admin WHERE username = :username")
                result = conn.execute(query, {"username": st.session_state.username}).fetchone()
                
                if result and pass_lama == result[0]:
                    update_query = text("""
                        UPDATE user_admin
                        SET password = :password
                        WHERE username = :username
                    """)
                    conn.execute(update_query, {"username": st.session_state.username, "password": pass_baru})
                    conn.commit()
                    st.success("Password successfully changed.")
                else:
                    st.error("Incorrect old password, please try again.")

def main():
    st.header('Admin Page') 
    if st.session_state.role == 'admin' : 
        menu_option = st.sidebar.selectbox("Admin Menu", ('Create User', 'Delete User', 'Change Password'))
    elif st.session_state.role == 'user' :
        menu_option = st.sidebar.selectbox("User Menu", ('Change Password',))
    
    if menu_option == 'Create User':
        create_user()
    elif menu_option == 'Delete User' :
        delete_user()
    elif menu_option == 'Change Password' :
        change_password()
if __name__ == '__main__':
    main()
