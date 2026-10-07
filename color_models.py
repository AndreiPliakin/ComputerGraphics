class RGB:
    def __init__(self, r=0, g=0, b=0):
        self.r = r
        self.g = g
        self.b = b

    def __repr__(self):
        return f"RGB({self.r}, {self.g}, {self.b})"


class CMYK:
    def __init__(self, c=0, m=0, y=0, k=1):
        self.c = c
        self.m = m
        self.y = y
        self.k = k

    def __repr__(self):
        return f"CMYK({self.c}, {self.m}, {self.y}, {self.k})"


class HSV:
    def __init__(self, h=0, s=0, v=0):
        self.h = h
        self.s = s
        self.v = v

    def __repr__(self):
        return f"HSV({self.h}, {self.s}, {self.v})"