import numpy as np

def otsu_threshold(gray: np.ndarray) -> tuple[np.ndarray, int]:
    hist = np.bincount(gray.ravel(), minlength=256).astype(np.float64)
    total = float(gray.size)
    sum_total = float(np.dot(np.arange(256), hist))

    sum_b = 0.0
    w_b = 0.0
    max_var = -1.0
    best_t = 0

    for t in range(256):
        w_b += hist[t]
        if w_b == 0.0:
            continue
        w_f = total - w_b
        if w_f == 0.0:
            break
        sum_b += t * hist[t]
        mu_b = sum_b / w_b
        mu_f = (sum_total - sum_b) / w_f
        var_between = w_b * w_f * (mu_b - mu_f) ** 2
        if var_between > max_var:
            max_var = var_between
            best_t = t

    result = np.where(gray > best_t, 255, 0).astype(np.uint8)
    return result, int(best_t)

def iterative_threshold(gray: np.ndarray, eps: float = 1.0) -> tuple[np.ndarray, float]:
    T = float(gray.mean())
    while True:
        low = gray[gray <= T]
        high = gray[gray > T]
        if low.size == 0 or high.size == 0:
            break
        T_new = (low.mean() + high.mean()) / 2.0
        if abs(T_new - T) < eps:
            T = T_new
            break
        T = T_new

    result = np.where(gray > T, 255, 0).astype(np.uint8)
    return result, float(T)