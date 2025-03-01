"""
Image processing functions for defect detection.
"""

import cv2
import numpy as np
import pandas as pd


def extract_image_data(result, confidence_threshold):
    """
    Extracts bounding box data from YOLO detection results and filters detections based on confidence threshold.

    Args:
                    result: YOLO detection result object.
                    confidence_threshold (float): Minimum confidence percentage to include a detection.

    Returns:
                    pd.DataFrame: DataFrame containing detected object details including ID, class, confidence, coordinates,
                                                                            and width/height in centimeters.
    """
    boxes = result.boxes
    class_ids = boxes.cls
    confidences = boxes.conf
    xywh = boxes.xywh

    data = []
    for i in range(len(class_ids)):
        confidence = confidences[i] * 100
        if confidence >= confidence_threshold:
            class_name = result.names[int(class_ids[i])]
            x_center, y_center, width, height = xywh[i]
            x0, y0 = int(x_center - width / 2), int(y_center - height / 2)
            x1, y1 = int(x_center + width / 2), int(y_center + height / 2)
            data.append(
                [
                    i + 1,
                    class_name,
                    f"{confidence:.2f} %",
                    x0,
                    x1,
                    y0,
                    y1,
                    f"{width/4:.2f}",
                    f"{height/4:.2f}",
                ]
            )

    return pd.DataFrame(
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


def annotate_image(result, df):
    """
    Annotates detected objects on the original image by drawing bounding boxes and labeling IDs.

    Args:
                    result: YOLO detection result object containing the original image.
                    df (pd.DataFrame): DataFrame containing detection details.

    Returns:
                    np.array: Annotated image as a NumPy array.
    """
    result_img = np.array(result.orig_img)
    for _, row in df.iterrows():
        x0, y0, x1, y1, id_label = row["x0"], row["y0"], row["x1"], row["y1"], row["ID"]
        label_x, label_y = x0 - 20, int(y0 + (y1 - y0) / 2)
        cv2.rectangle(result_img, (x0, y0), (x1, y1), (0, 255, 0), 2)
        cv2.putText(
            result_img,
            str(id_label),
            (label_x, label_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            2,
        )
    return result_img
