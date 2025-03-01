"""
Video processing functions for defect detection.
"""

import os
import tempfile
import time

import cv2
import streamlit as st

from .image_processing import annotate_image, extract_image_data


def load_video(uploaded_file):
    """
    Saves an uploaded video file temporarily to disk.

    Args:
        uploaded_file: Streamlit file uploader object for video.

    Returns:
        str: Path to the saved temporary video file.
    """
    video_bytes = uploaded_file.read()
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    temp_file.write(video_bytes)
    temp_file.flush()
    return temp_file.name


def process_frame(frame, model, confidence_threshold):
    """
    Processes a single video frame by performing YOLO inference and annotating detected objects.

    Args:
                    frame (np.array): Video frame image.
                    model: YOLO object detection model.
                    confidence_threshold (float): Minimum confidence level for detections.

    Returns:
                    tuple: Annotated frame and extracted detection data as a DataFrame.
    """
    results = model(frame)
    defects_data = extract_image_data(results[0], confidence_threshold)
    return annotate_image(results[0], defects_data), defects_data


def process_video(
    uploaded_file,
    model,
    result_video_placeholder,
    metrics_placeholder,
    defects_placeholder,
    duration_placeholder,
    confidence_threshold,
):
    """
    Processes an uploaded video file, performing YOLO inference on each frame while maintaining real-time performance.

    Args:
        uploaded_file: Streamlit file uploader object for video.
        model: YOLO object detection model.
        result_video_placeholder: Streamlit placeholder for displaying processed video frames.
        metrics_placeholder: Streamlit placeholder for displaying FPS and performance metrics.
        defects_placeholder: Streamlit placeholder for displaying defect data.
        duration_placeholder: Streamlit placeholder for displaying video processing duration.
        confidence_threshold (float): Minimum confidence level for detections.
    """
    temp_file_path = load_video(uploaded_file)
    video_capture = cv2.VideoCapture(temp_file_path)

    if not video_capture.isOpened():
        st.error("Error: Unable to open video file.")
        return

    frame_rate = int(video_capture.get(cv2.CAP_PROP_FPS))
    total_frames = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
    start_time, frame_index = time.time(), 0
    frames_skipped, frames_displayed = 0, 0
    prev_frame_time = start_time

    while video_capture.isOpened():
        ret, frame = video_capture.read()
        if not ret or frame_index >= total_frames:
            break

        frame_processing_start = time.time()
        result_img, defects_data_frame = process_frame(
            frame, model, confidence_threshold
        )
        frame_processing_time = time.time() - frame_processing_start

        time_since_last_frame = time.time() - prev_frame_time
        display_fps = 1 / time_since_last_frame if time_since_last_frame > 0 else 0
        prev_frame_time = time.time()

        result_video_placeholder.image(result_img, channels="RGB")

        # Calculate total frames passed (skipped + displayed)
        total_frames_passed = frames_skipped + frames_displayed

        # Avoid division by zero
        if total_frames_passed > 0:
            frames_skipped_percentage = (frames_skipped * 100) / total_frames_passed
            frames_displayed_percentage = (frames_displayed * 100) / total_frames_passed
        else:
            frames_skipped_percentage = 0
            frames_displayed_percentage = 0

        duration_placeholder.text(f"Video Duration: {time.time() - start_time:.2f} sec")
        metrics_placeholder.text(
            f"Original FPS: {frame_rate}\n"
            f"Display FPS: {display_fps:.2f}\n"
            f"Processing Time per Frame: {frame_processing_time:.3f} sec\n"
            f"Frames Skipped: {frames_skipped}/{total_frames_passed} ({frames_skipped_percentage:.2f}%)\n"
            f"Frames Displayed: {frames_displayed}/{total_frames_passed} ({frames_displayed_percentage:.2f}%)\n"
        )
        defects_placeholder.dataframe(defects_data_frame)

        elapsed_real_time = time.time() - start_time
        expected_frame_index = int(elapsed_real_time * frame_rate)
        if expected_frame_index > frame_index:
            frames_skipped += expected_frame_index - frame_index - 1
            frame_index = expected_frame_index
        frames_displayed += 1
        video_capture.set(cv2.CAP_PROP_POS_FRAMES, frame_index)

    video_capture.release()
    os.remove(temp_file_path)
