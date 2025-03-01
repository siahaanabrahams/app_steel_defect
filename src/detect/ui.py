"""
UI functions for image and video detection.
"""

import streamlit as st
from PIL import Image

from .image_processing import annotate_image, extract_image_data
from .video_processing import process_video


def setup_ui(model):
    """
    Configures the Streamlit UI for image and video detection.

    Args:
        model (YOLO): Loaded YOLO model.

    Returns:
        None
    """
    file_type = st.sidebar.selectbox("Select file type", ["Image", "Video"], index=1)
    uploaded_file = st.sidebar.file_uploader(
        "Upload a file", type=["png", "jpg", "jpeg", "mp4", "mov", "avi"]
    )
    confidence_level = st.sidebar.slider(
        "Confidence Level", min_value=0, max_value=100, step=10
    )

    if uploaded_file:
        if file_type == "Image":
            st.header("Image Detection")
            image = Image.open(uploaded_file)
            result = model(image, conf=confidence_level / 100)[0]
            data = extract_image_data(result, confidence_level)
            result_img = annotate_image(result, data)

            col1, col2 = st.columns(2)
            with col1:
                st.image(image, caption="Upload")
            with col2:
                st.image(result_img, caption="Result")
            st.write("Detection Details")
            st.dataframe(data)

        elif file_type == "Video":
            st.header("Video Detection")
            if st.button("Start Video"):
                col1, col2 = st.columns(2)
                with col1:
                    st.video(uploaded_file)
                with col2:
                    result_video_placeholder = st.empty()

                duration_placeholder, metrics_placeholder, defects_placeholder = (
                    st.empty(),
                    st.empty(),
                    st.empty(),
                )
                process_video(
                    uploaded_file,
                    model,
                    result_video_placeholder,
                    metrics_placeholder,
                    defects_placeholder,
                    duration_placeholder,
                    confidence_level,
                )
