from color_models import RGB, CMYK, HSV
from conversions import (
    rgb_to_cmyk,
    cmyk_to_rgb,
    rgb_to_hsv,
    hsv_to_rgb
)


class ColorState:
    def __init__(self, rgb=None):
        if rgb is None:
            rgb = RGB(0, 0, 0)

        self.rgb = rgb
        self.cmyk = rgb_to_cmyk(rgb)
        self.hsv = rgb_to_hsv(rgb)

    def set_rgb(self, rgb):
        self.rgb = rgb
        self.cmyk = rgb_to_cmyk(rgb)
        self.hsv = rgb_to_hsv(rgb)

    def set_cmyk(self, cmyk):
        self.cmyk = cmyk
        self.rgb = cmyk_to_rgb(cmyk)
        self.hsv = rgb_to_hsv(self.rgb)

    def set_hsv(self, hsv):
        self.hsv = hsv
        self.rgb = hsv_to_rgb(hsv)
        self.cmyk = rgb_to_cmyk(self.rgb)