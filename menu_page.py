import streamlit as st
import page_main
import page_detect
import page_admin
from sqlalchemy import create_engine, text 

DB_URL = "postgresql+pg8000://postgres:abraham@localhost:5432/postgres"
engine = create_engine(DB_URL)

def main():  
    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        st.warning("Please log in first.")
        return
    
    menu_option = st.sidebar.selectbox("Pilih Menu", ("Main Page", "Detect", "Admin Page"))

    if menu_option == 'Main Page': 
        page_main.main()
    elif menu_option == 'Detect': 
        page_detect.main()
    elif menu_option == 'Admin Page' :
        page_admin.main()

    if st.sidebar.button("Logout"):
        id = st.session_state.id_user
        st.session_state.logged_in = False
        st.session_state.username = ''
        with engine.connect() as conn :
            query = text("""
                         SELECT id_operation 
                         FROM operation 
                         WHERE id_user = :id 
                         ORDER BY start_time DESC 
                         LIMIT 1""")
            id_operation = conn.execute(query, {"id" : id}).fetchone()
        id_operation = id_operation[0]
        with engine.connect() as conn : 
            query = text("UPDATE operation SET end_time = NOW() WHERE id_operation= :id_operation")
            conn.execute(query, {"id_operation" : id_operation})
            conn.commit()
        st.experimental_rerun()   
