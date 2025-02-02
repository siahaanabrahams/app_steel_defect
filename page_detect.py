import streamlit as st
from ultralytics import YOLO
from PIL import Image
import pandas as pd
import numpy as np
import cv2
import os
import tempfile
import time

if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.uploaded_file = None


# IMAGE PROCESS
def image_data(result, confidence_threshold):
    boxes = result.boxes
    class_ids = boxes.cls
    confidences = boxes.conf
    xywh = boxes.xywh

    data = []
    for i in range(len(class_ids)):
        confidence = confidences[i] * 100  # Convert to percentage
        if confidence >= confidence_threshold:
            class_name = result.names[int(class_ids[i])]
            x_center, y_center, width, height = xywh[i]
            x0, y0 = int(x_center - width / 2), int(y_center - height / 2)
            x1, y1 = int(x_center + width / 2), int(y_center + height / 2)
            confidence = f"{confidence:.2f} %"
            width = f"{width/4:.2f}"
            height = f"{height/4:.2f}"
            data.append([i + 1, class_name, confidence, x0, x1, y0, y1, width, height])
    df = pd.DataFrame(
        data,
        columns=[
            "ID",
            "Class",
            "Confidence",
            "x0",
            "x1",
            "y0",
            "y1",
            "Width (cm)",
            "Height (cm)",
        ],
    )
    return df


def image_plot(result, df):
    result_img = np.array(result.orig_img)
    for i, row in df.iterrows():
        x0, y0, x1, y1 = row["x0"], row["y0"], row["x1"], row["y1"]
        id_label = row["ID"]
        label_x = x0 - 20
        label_y = int(y0 + (y1 - y0) / 2)
        result_img = cv2.rectangle(result_img, (x0, y0), (x1, y1), (0, 255, 0), 2)
        result_img = cv2.putText(
            result_img,
            str(id_label),
            (label_x, label_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            2,
        )
    return result_img


# VIDEO PROCESS
def video_process(
    uploaded_file,
    model,
    result_video_placeholder,
    metrics_placeholder,
    defects_placeholder,
    duration_placeholder,
    confidence_threshold,
):
    video_bytes = uploaded_file.read()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
        temp_file.write(video_bytes)
        temp_file.flush()
        temp_file_path = temp_file.name

    if not os.path.exists(temp_file_path):
        st.error(f"Error: Temporary file not found at {temp_file_path}")
        return

    try:
        video_capture = cv2.VideoCapture(temp_file_path)
        if not video_capture.isOpened():
            st.error("Error: Unable to open video file.")
            return
    except Exception as e:
        st.error(f"Error loading video: {e}")
        return

    # Retrieve video properties
    frame_rate = int(video_capture.get(cv2.CAP_PROP_FPS))
    total_frames = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
    video_duration = total_frames / frame_rate

    # Initialize variables
    frame_index = 0
    start_time = time.time()
    processed_frames = 0
    frames_skipped = 0
    frames_displayed = 0
    prev_frame_time = start_time  # For FPS calculation
    frame_processing_time = 0  # Initialize here

    frame_placeholder = st.empty()

    while video_capture.isOpened():
        ret, frame = video_capture.read()
        if not ret or frame_index >= total_frames:
            break

        # Start timing frame processing
        frame_processing_start = time.time()

        # Run YOLO model on the frame
        results = model(frame)
        annotated_frame = results[0].plot()
        defects_data = image_data(results[0], confidence_threshold)

        # Update processed frames count
        processed_frames += 1

        # Calculate processing time for the current frame
        frame_processing_time = time.time() - frame_processing_start

        # Calculate FPS based on frame display rate
        time_since_last_frame = time.time() - prev_frame_time
        if time_since_last_frame > 0:
            display_fps = 1 / time_since_last_frame
        else:
            display_fps = 0

        # Update previous frame time
        prev_frame_time = time.time()

        # Process the detection details and plot on the frame
        defects_data_frame = image_data(results[0], confidence_threshold)
        result_img = image_plot(results[0], defects_data_frame)

        # Display annotated frame and defects data
        result_video_placeholder.image(
            result_img, channels="RGB", use_container_width=True
        )

        # Calculate total frames passed (skipped + displayed)
        total_frames_passed = frames_skipped + frames_displayed

        # Avoid division by zero
        if total_frames_passed > 0:
            frames_skipped_percentage = (frames_skipped * 100) / total_frames_passed
            frames_displayed_percentage = (frames_displayed * 100) / total_frames_passed
        else:
            frames_skipped_percentage = 0
            frames_displayed_percentage = 0

        # Display metrics first
        metrics_placeholder.text(
            f"Original FPS: {frame_rate}\n"
            f"Display FPS: {display_fps:.2f}\n"
            f"Processing Time per Frame: {frame_processing_time:.3f} seconds\n"
            f"Frames Skipped: {frames_skipped}/{total_frames_passed} ({frames_skipped_percentage:.2f}%)\n"
            f"Frames Displayed: {frames_displayed}/{total_frames_passed} ({frames_displayed_percentage:.2f}%)\n"
        )

        # Display defects data after metrics
        defects_placeholder.dataframe(defects_data_frame, use_container_width=True)

        # Display video duration in seconds
        duration_placeholder.text(
            f"Video Duration: {time.time() - start_time:.2f} seconds"
        )

        # Skip frames to synchronize playback duration
        elapsed_real_time = time.time() - start_time
        expected_frame_index = int(elapsed_real_time * frame_rate)

        if expected_frame_index > frame_index:
            frames_skipped += expected_frame_index - frame_index - 1
            frame_index = expected_frame_index

        frames_displayed += 1
        video_capture.set(cv2.CAP_PROP_POS_FRAMES, frame_index)

    video_capture.release()
    os.remove(temp_file_path)


model = YOLO("weight-merged.pt")

file_type = st.sidebar.selectbox("Select file type", ["Image", "Video"], index=1)
uploaded_file = None

if file_type == "Image":
    uploaded_file = st.sidebar.file_uploader(
        "Upload an image", type=["png", "jpg", "jpeg"]
    )

elif file_type == "Video":
    uploaded_file = st.sidebar.file_uploader(
        "Upload a video", type=["mp4", "mov", "avi"]
    )

confidence_level = st.sidebar.slider(
    "Confidence Level", min_value=0, max_value=100, step=10
)

if uploaded_file is not None:
    if file_type == "Image":
        st.header("Image Detection")
        image = Image.open(uploaded_file)
        result = model(image, conf=confidence_level / 100)
        result = result[0]
        data = image_data(result, confidence_level)
        result_img = image_plot(result, data)
        col1, col2 = st.columns(2)
        with col1:
            st.image(image, caption="Upload")
        with col2:
            st.image(result_img, caption="Result")
        st.write("Detection Details")
        st.dataframe(data, use_container_width=True)

    elif file_type == "Video":
        st.header("Video Detection")
        start_button = st.button("Start Video")

        if start_button:
            col1, col2 = st.columns(2)  # Separate the videos
            with col1:
                st.video(uploaded_file)
            with col2:
                result_video_placeholder = (
                    st.empty()
                )  # Placeholder for the result video processing
                duration_placeholder = st.empty()  # Placeholder for video duration

            # First create placeholders in the desired order
            st.subheader("Detection Metrics and Details")
            metrics_placeholder = st.empty()  # Metrics will appear first
            defects_placeholder = st.empty()  # Defects table will appear second

            # Process video with the new order of placeholders
            video_process(
                uploaded_file,
                model,
                result_video_placeholder,
                metrics_placeholder,
                defects_placeholder,
                duration_placeholder,
                confidence_level,
            )
