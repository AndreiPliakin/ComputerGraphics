import os
import cv2
import numpy as np
from PyQt5 import QtGui
from PyQt5.QtCore import Qt

IMAGES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff")

def list_image_files() -> list[str]:
    if not os.path.isdir(IMAGES_DIR):
        return []
    return sorted(
        name for name in os.listdir(IMAGES_DIR)
        if name.lower().endswith(IMAGE_EXTENSIONS)
    )

def load_image_gray(path: str) -> np.ndarray | None:
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return None
    if img.dtype != np.uint8:
        img = np.clip(img, 0, 255).astype(np.uint8)
    return img

def save_image(path: str, img: np.ndarray) -> bool:
    return bool(cv2.imwrite(path, img))

def np_to_qpixmap(img: np.ndarray, max_size: int = 460) -> QtGui.QPixmap:
    if img.ndim == 2:
        img_rgb = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    else:
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    h, w, ch = img_rgb.shape
    qimg = QtGui.QImage(
        img_rgb.data, w, h, ch * w, QtGui.QImage.Format_RGB888
    ).copy()
    return QtGui.QPixmap.fromImage(qimg).scaled(
        max_size, max_size,
        Qt.KeepAspectRatio,
        Qt.SmoothTransformation,
    )