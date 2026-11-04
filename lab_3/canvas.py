from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush
from PyQt5.QtCore import Qt, QPoint


class RasterCanvas(QWidget):
    MIN_CELL = 2
    MAX_CELL = 500

    def __init__(self, parent=None):
        super().__init__(parent)
        self.cell = 30
        self.points = []
        self.show_centers = False
        self.setMinimumSize(700, 700)
        self.setAutoFillBackground(True)
        self.setStyleSheet("background:white;")

    def set_points(self, pts):
        self.points = list(pts)
        self.update()

    def set_cell(self, cell):
        self.cell = max(self.MIN_CELL, min(self.MAX_CELL, int(cell)))
        self.update()

    def zoom(self, factor):
        self.set_cell(int(self.cell * factor))

    def fit(self, margin_ratio=0.15, scale=0.6):
        if not self.points:
            return
        xs = [p[0] for p in self.points]
        ys = [p[1] for p in self.points]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        dx = max(1, max_x - min_x)
        dy = max(1, max_y - min_y)
        w = self.width() * (1 - 2 * margin_ratio)
        h = self.height() * (1 - 2 * margin_ratio)
        cell = int(min(w / dx, h / dy) * scale)
        self.set_cell(cell)

    def _origin(self):
        return self.width() // 2, self.height() // 2

    def _to_screen(self, i, j):
        cx, cy = self._origin()
        return QPoint(int(cx + (i + 0.5) * self.cell),
                      int(cy - (j + 0.5) * self.cell))

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, False)
        w, h = self.width(), self.height()
        cx, cy = self._origin()
        cell = self.cell

        p.setPen(QPen(QColor(232, 232, 232), 1))
        for x in range(cx % cell, w + cell, cell):
            p.drawLine(x, 0, x, h)
        for y in range(cy % cell, h + cell, cell):
            p.drawLine(0, y, w, y)

        p.setPen(QPen(QColor(60, 60, 60), 2))
        p.drawLine(0, cy, w, cy)
        p.drawLine(cx, 0, cx, h)

        p.setPen(QColor(60, 60, 60))
        p.drawText(w - 16, cy - 8, "X")
        p.drawText(cx + 8, 16, "Y")

        step_labels = 1
        while step_labels * cell < 60:
            step_labels += 1
        nice = 1
        for n in (1, 2, 5, 10, 20, 50, 100, 200, 500):
            if step_labels <= n:
                nice = n
                break
        else:
            nice = step_labels

        p.setPen(QColor(80, 80, 80))
        font = p.font()
        font.setPointSize(8)
        p.setFont(font)
        fm = p.fontMetrics()
        text_h = fm.height()

        i_min = -(cx // cell)
        i_max = (w - cx) // cell + 1
        for i in range(i_min, i_max + 1):
            if i == 0 or i % nice != 0:
                continue
            x = cx + i * cell
            p.drawLine(x, cy - 4, x, cy + 4)
            label = str(i)
            tw = fm.horizontalAdvance(label)
            p.drawText(x - tw // 2, cy + 6 + text_h, label)

        j_min = -((h - cy) // cell)
        j_max = cy // cell + 1
        for j in range(j_min, j_max + 1):
            if j == 0 or j % nice != 0:
                continue
            y = cy - j * cell
            p.drawLine(cx - 4, y, cx + 4, y)
            label = str(j)
            p.drawText(cx + 6, y + fm.ascent() // 2 - 1, label)

        p.drawText(cx + 6, cy + 6 + fm.ascent(), "0")

        if self.points:
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(QColor(220, 50, 50)))
            for (i, j) in self.points:
                sp = self._to_screen(i, j)
                p.drawRect(int(sp.x() - cell / 2),
                           int(sp.y() - cell / 2),
                           cell, cell)

        if self.show_centers:
            p.setPen(QPen(QColor(0, 0, 0), 1))
            p.setBrush(QColor(0, 0, 0))
            for (i, j) in self.points:
                sp = self._to_screen(i, j)
                p.drawEllipse(sp, 2, 2)