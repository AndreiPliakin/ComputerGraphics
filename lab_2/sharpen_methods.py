import numpy as np
import cv2

def laplacian_sharpen(gray: np.ndarray, gain: float = 1.0) -> np.ndarray:
    kernel = np.array([[0,  1, 0],
                       [1, -4, 1],
                       [0,  1, 0]], dtype=np.float64)

    h, w = gray.shape
    padded = np.pad(gray.astype(np.float64), 1, mode="edge")
    lap = np.zeros((h, w), dtype=np.float64)

    for i in range(3):
        for j in range(3):
            k = kernel[i, j]
            if k != 0.0:
                lap += k * padded[i:i + h, j:j + w]

    sharp = gray.astype(np.float64) - gain * lap
    return np.clip(sharp, 0, 255).astype(np.uint8)

def unsharp_mask(gray: np.ndarray, sigma: float = 3.0, k: float = 1.0) -> np.ndarray:
    blurred = cv2.GaussianBlur(gray, (0, 0), sigma)
    mask = gray.astype(np.float64) - blurred.astype(np.float64)
    sharp = gray.astype(np.float64) + k * mask
    return np.clip(sharp, 0, 255).astype(np.uint8)