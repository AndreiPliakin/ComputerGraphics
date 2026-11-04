def dda(x1, y1, x2, y2):
    points = []
    dx = x2 - x1
    dy = y2 - y1
    steps = max(abs(dx), abs(dy))
    if steps == 0:
        return [(x1, y1)]
    x_inc = dx / steps
    y_inc = dy / steps
    x, y = float(x1), float(y1)
    for _ in range(steps + 1):
        points.append((int(x + 0.5), int(y + 0.5)))
        x += x_inc
        y += y_inc
    return points
