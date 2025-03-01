"""
Streamlit app for image and video detection.
"""

import streamlit as st

from .model_loader import load_yolo_model
from .ui import setup_ui


def main():
    """
    Main function to initialize the Streamlit app and load the YOLO model.
    """
    st.session_state.setdefault("initialized", True)
    st.session_state.setdefault("uploaded_file", None)
    model = load_yolo_model("weights/weight-merged.pt")
    setup_ui(model)


if __name__ == "__main__":
    main()
