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

def main() :
    # IMAGE PROCESS
    def image_data(result):
        boxes = result.boxes
        class_ids = boxes.cls
        confidences = boxes.conf
        xywh = boxes.xywh

        data = []
        for i in range(len(class_ids)):
            class_name = result.names[int(class_ids[i])]
            confidence = confidences[i]
            x_center, y_center, width, height = xywh[i]
            x0, y0 = int(x_center - width / 2), int(y_center - height / 2)
            x1, y1 = int(x_center + width / 2), int(y_center + height / 2)
            confidence = confidence * 100
            confidence = f"{confidence:.2f} %"
            width = f"{width:.2f}"
            height = f"{height:.2f}"
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
    def video_process(uploaded_file, model):
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

        frame_placeholder = st.empty()
        duration_placeholder = st.empty()
        metrics_placeholder = st.empty()

        # Initialize variables
        frame_index = 0
        start_time = time.time()
        processed_frames = 0

        while video_capture.isOpened():
            ret, frame = video_capture.read()
            if not ret or frame_index >= total_frames:
                break

            # Start timing frame processing
            frame_processing_start = time.time()

            # Run YOLO model on the frame
            results = model(frame)
            annotated_frame = results[0].plot()

            # Update processed frames count
            processed_frames += 1

            # Calculate the actual elapsed time since playback started
            elapsed_real_time = time.time() - start_time

            # Determine the expected frame index based on elapsed real-time
            expected_frame_index = int(elapsed_real_time * frame_rate)

            # Update the video frame in Streamlit
            frame_placeholder.image(
                annotated_frame, channels="RGB"
            )

            # Calculate processing time for the current frame
            frame_processing_time = time.time() - frame_processing_start
            current_fps = (
                processed_frames / elapsed_real_time if elapsed_real_time > 0 else 0
            )

            # Display metrics
            formatted_elapsed_time = time.strftime(
                "%H:%M:%S", time.gmtime(elapsed_real_time)
            )
            formatted_total_duration = time.strftime(
                "%H:%M:%S", time.gmtime(video_duration)
            )
            duration_placeholder.text(
                f"Elapsed Time: {formatted_elapsed_time} / {formatted_total_duration}"
            )
            metrics_placeholder.text(
                f"Original FPS: {frame_rate}\n"
                f"Current FPS: {current_fps:.2f}\n"
                f"Processing Time per Frame: {frame_processing_time:.3f} seconds"
            )

            # Skip frames to synchronize playback duration
            frame_index = max(expected_frame_index, frame_index + 1)
            video_capture.set(cv2.CAP_PROP_POS_FRAMES, frame_index)

        video_capture.release()
        os.remove(temp_file_path)


    # MODEL LOAD
    model = YOLO("weight.pt")

    # SIDEBAR
    file_type = st.sidebar.selectbox("Select file type", ["Image", "Video"])
    uploaded_file = None

    if file_type == "Image":
        uploaded_file = st.sidebar.file_uploader(
            "Upload an image", type=["png", "jpg", "jpeg"]
        )

    elif file_type == "Video":
        uploaded_file = st.sidebar.file_uploader(
            "Upload a video", type=["mp4", "mov", "avi"]
        )

    # Confidence Level
    confidence_level = st.sidebar.slider(
        "Confidence Level", min_value=0, max_value=100, step=10
    )

    # MAIN PAGE
    if uploaded_file is not None:
        if file_type == "Image":
            st.header("Image Detection")
            image = Image.open(uploaded_file)
            result = model(image, conf=confidence_level / 100)
            result = result[0]
            data = image_data(result)
            result_img = image_plot(result, data)
            col1, col2 = st.columns(2)
            with col1:
                st.image(image, caption="Upload")
            with col2:
                st.image(result_img, caption="Result")
            st.write(data)

        elif file_type == "Video":
            st.header("Video Detection")

            # Place the Start button above the video
            start_button = st.button("Start Video")

            if start_button:
                st.empty()  # Removes the Start button after it's clicked

                # Display video
                col1, col2 = st.columns(2)
                with col1:
                    st.video(uploaded_file)
                with col2:
                    video_process(uploaded_file, model)