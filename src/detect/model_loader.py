from ultralytics import YOLO


def load_yolo_model(model):
    """
    Loads the YOLO object detection model with pre-trained weights.

    Returns:
        YOLO: An instance of the YOLO model.
    """
    return YOLO(model)
