def bresenham_circle(cx, cy, r):
    pts = set()
    if r < 0:
        return []
    if r == 0:
        return [(cx, cy)]

    def plot(x, y):
        pts.add((cx + x, cy + y))
        pts.add((cx - x, cy + y))
        pts.add((cx + x, cy - y))
        pts.add((cx - x, cy - y))
        pts.add((cx + y, cy + x))
        pts.add((cx - y, cy + x))
        pts.add((cx + y, cy - x))
        pts.add((cx - y, cy - x))

    x, y = 0, r
    d = 3 - 2 * r
    plot(x, y)
    while y >= x:
        x += 1
        if d > 0:
            y -= 1
            d += 4 * (x - y) + 10
        else:
            d += 4 * x + 6
        plot(x, y)
    return list(pts)
