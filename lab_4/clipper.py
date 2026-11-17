import math


EPS = 1e-9


def read_input(path):
    with open(path, encoding="utf-8") as file:
        data = list(map(float, file.read().split()))

    pos = 0
    n = int(data[pos])
    pos += 1

    segments = [
        tuple(data[pos + i:pos + i + 4])
        for i in range(0, 4 * n, 4)
    ]
    pos += 4 * n

    xmin, ymin, xmax, ymax = data[pos:pos + 4]
    pos += 4

    polygon = None
    if pos < len(data):
        m = int(data[pos])
        pos += 1
        polygon = [
            tuple(data[pos + 2 * i:pos + 2 * i + 2])
            for i in range(m)
        ]
        validate_convex_polygon(polygon)

    return segments, (xmin, ymin, xmax, ymax), polygon


def liang_barsky(x1, y1, x2, y2, xmin, ymin, xmax, ymax):
    dx = x2 - x1
    dy = y2 - y1
    t_enter = 0.0
    t_exit = 1.0

    checks = [
        (-dx, x1 - xmin),
        (dx, xmax - x1),
        (-dy, y1 - ymin),
        (dy, ymax - y1),
    ]

    for p, q in checks:
        if abs(p) < EPS:
            if q < -EPS:
                return None
            continue

        t = q / p

        if p < 0:
            if t > t_exit + EPS:
                return None
            t_enter = max(t_enter, t)
        else:
            if t < t_enter - EPS:
                return None
            t_exit = min(t_exit, t)

    if t_enter > t_exit + EPS:
        return None

    return (
        x1 + t_enter * dx,
        y1 + t_enter * dy,
        x1 + t_exit * dx,
        y1 + t_exit * dy,
    )


def signed_area(polygon):
    return sum(
        polygon[i][0] * polygon[(i + 1) % len(polygon)][1]
        - polygon[(i + 1) % len(polygon)][0] * polygon[i][1]
        for i in range(len(polygon))
    ) / 2.0


def validate_convex_polygon(polygon):
    if len(polygon) < 3 or abs(signed_area(polygon)) < EPS:
        raise ValueError("Некорректный многоугольник")

    orientation = 0
    n = len(polygon)

    for i in range(n):
        ax, ay = polygon[i]
        bx, by = polygon[(i + 1) % n]
        cx, cy = polygon[(i + 2) % n]

        cross = (
            (bx - ax) * (cy - by)
            - (by - ay) * (cx - bx)
        )

        if abs(cross) < EPS:
            continue

        current = 1 if cross > 0 else -1

        if orientation == 0:
            orientation = current
        elif orientation != current:
            raise ValueError("Многоугольник должен быть выпуклым")

    if orientation == 0:
        raise ValueError("Вырожденный многоугольник")


def clip_segment_by_convex_polygon(x1, y1, x2, y2, polygon):
    if polygon is None or len(polygon) < 3:
        return None

    area = signed_area(polygon)

    if abs(area) < EPS:
        return None

    orientation = 1.0 if area > 0 else -1.0
    dx = x2 - x1
    dy = y2 - y1
    t_enter = 0.0
    t_exit = 1.0

    for i in range(len(polygon)):
        ax, ay = polygon[i]
        bx, by = polygon[(i + 1) % len(polygon)]

        ex = bx - ax
        ey = by - ay

        f0 = orientation * (
            ex * (y1 - ay) - ey * (x1 - ax)
        )
        fd = orientation * (ex * dy - ey * dx)

        if abs(fd) < EPS:
            if f0 < -EPS:
                return None
            continue

        t = -f0 / fd

        if fd > 0:
            t_enter = max(t_enter, t)
        else:
            t_exit = min(t_exit, t)

        if t_enter > t_exit + EPS:
            return None

    return (
        x1 + t_enter * dx,
        y1 + t_enter * dy,
        x1 + t_exit * dx,
        y1 + t_exit * dy,
    )