from color_models import RGB, CMYK, HSV


def rgb_to_cmyk(rgb):
    r = rgb.r / 255
    g = rgb.g / 255
    b = rgb.b / 255

    k = 1 - max(r, g, b)

    if k == 1:
        return CMYK(0.0, 0.0, 0.0, 1.0)

    c = (1 - r - k) / (1 - k)
    m = (1 - g - k) / (1 - k)
    y = (1 - b - k) / (1 - k)

    return CMYK(c, m, y, k)


def cmyk_to_rgb(cmyk):
    c = cmyk.c
    m = cmyk.m
    y = cmyk.y
    k = cmyk.k

    r = 255 * (1 - c) * (1 - k)
    g = 255 * (1 - m) * (1 - k)
    b = 255 * (1 - y) * (1 - k)

    return RGB(r, g, b)


def rgb_to_hsv(rgb):
    r = rgb.r / 255
    g = rgb.g / 255
    b = rgb.b / 255

    max_value = max(r, g, b)
    min_value = min(r, g, b)

    delta = max_value - min_value

    if delta == 0:
        h = 0.0

    elif max_value == r:
        h = 60 * (((g - b) / delta) % 6)

    elif max_value == g:
        h = 60 * (((b - r) / delta) + 2)

    else:
        h = 60 * (((r - g) / delta) + 4)

    if max_value == 0:
        s = 0.0
    else:
        s = delta / max_value

    v = max_value

    return HSV(h, s, v)


def hsv_to_rgb(hsv):
    h = hsv.h % 360
    s = hsv.s
    v = hsv.v

    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c

    sector = int(h / 60)

    match sector:
        case 0:
            r1, g1, b1 = c, x, 0
        case 1:
            r1, g1, b1 = x, c, 0
        case 2:
            r1, g1, b1 = 0, c, x
        case 3:
            r1, g1, b1 = 0, x, c
        case 4:
            r1, g1, b1 = x, 0, c
        case _:
            r1, g1, b1 = c, 0, x

    r = 255 * (r1 + m)
    g = 255 * (g1 + m)
    b = 255 * (b1 + m)

    return RGB(r, g, b)