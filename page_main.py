import streamlit as st

def main() :
    st.header(f"Welcome, {st.session_state.username}!")
    st.subheader('Steel Surface Defect Detection App')