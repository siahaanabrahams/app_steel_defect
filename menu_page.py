import streamlit as st
import page_main
import page_detect
import page_admin

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
        st.session_state.logged_in = False
        st.session_state.username = ''
        st.experimental_rerun()   
