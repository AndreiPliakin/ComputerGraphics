import math

from PyQt5.QtCore import Qt, QPointF, QRectF
from PyQt5.QtGui import QColor, QPainter, QPen
from PyQt5.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

import clipper


DEFAULT_SEGMENTS = [
    (-8, -8, 8, 8),
    (-9, 0, 9, 0),
    (0, -9, 0, 9),
    (-6, 2, 6, 2),
    (-4, -4, 4, 4),
    (10, 10, 15, 15),
    (-12, -3, -7, -3),
    (2, -6, 2, 6),
    (-5, 5, 5, -5),
    (-1, 7, 1, -7),
]

DEFAULT_RECT = (-5, -3, 5, 3)

DEFAULT_POLYGON = [
    (-3, -4),
    (3, -4),
    (4, 0),
    (2, 3),
    (-2, 3),
    (-4, 0),
]


class Canvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.segments = []
        self.clip_rect = None
        self.polygon = None
        self.mode = "rectangle"

        self.setMinimumSize(700, 550)

    def set_data(self, segments, clip_rect, polygon):
        self.segments = segments
        self.clip_rect = clip_rect
        self.polygon = polygon
        self.update()

    def _bounds(self):
        xs = []
        ys = []

        for x1, y1, x2, y2 in self.segments:
            xs.extend((x1, x2))
            ys.extend((y1, y2))

        if self.mode in ("rectangle", "both") and self.clip_rect:
            xmin, ymin, xmax, ymax = self.clip_rect
            xs.extend((xmin, xmax))
            ys.extend((ymin, ymax))

        if self.mode in ("polygon", "both") and self.polygon:
            for x, y in self.polygon:
                xs.append(x)
                ys.append(y)

        if not xs:
            return -1, -1, 1, 1

        xmin, xmax = min(xs), max(xs)
        ymin, ymax = min(ys), max(ys)

        if xmin == xmax:
            xmin -= 1
            xmax += 1

        if ymin == ymax:
            ymin -= 1
            ymax += 1

        pad_x = max((xmax - xmin) * 0.12, 1)
        pad_y = max((ymax - ymin) * 0.12, 1)

        return (
            xmin - pad_x,
            ymin - pad_y,
            xmax + pad_x,
            ymax + pad_y,
        )

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), Qt.white)

        xmin, ymin, xmax, ymax = self._bounds()

        margin = 25
        width = self.width() - 2 * margin
        height = self.height() - 2 * margin

        scale = min(
            width / (xmax - xmin),
            height / (ymax - ymin),
        )

        offset_x = (self.width() - (xmax - xmin) * scale) / 2
        offset_y = (self.height() - (ymax - ymin) * scale) / 2

        def tx(x):
            return offset_x + (x - xmin) * scale

        def ty(y):
            return self.height() - offset_y - (y - ymin) * scale

        self._draw_grid(painter, xmin, ymin, xmax, ymax, tx, ty)
        self._draw_source(painter, tx, ty)

        if self.mode in ("rectangle", "both"):
            self._draw_rectangle(painter, tx, ty)

        if self.mode in ("polygon", "both"):
            self._draw_polygon(painter, tx, ty)

        if self.mode in ("rectangle", "both"):
            self._draw_rectangle_result(painter, tx, ty)

        if self.mode in ("polygon", "both"):
            self._draw_polygon_result(painter, tx, ty)

        painter.end()

    def _draw_grid(self, painter, xmin, ymin, xmax, ymax, tx, ty):
        span = max(xmax - xmin, ymax - ymin)
        step = 1

        while span / step > 25:
            step *= 2

        while span / step < 10:
            step /= 2

        grid_pen = QPen(QColor(225, 225, 225), 1)
        painter.setPen(grid_pen)

        x = math.floor(xmin / step) * step
        while x <= xmax:
            px = round(tx(x))
            painter.drawLine(px, 0, px, self.height())
            x += step

        y = math.floor(ymin / step) * step
        while y <= ymax:
            py = round(ty(y))
            painter.drawLine(0, py, self.width(), py)
            y += step

        axis_pen = QPen(QColor(130, 130, 130), 1.5)
        painter.setPen(axis_pen)

        if ymin <= 0 <= ymax:
            py = round(ty(0))
            painter.drawLine(0, py, self.width(), py)

        if xmin <= 0 <= xmax:
            px = round(tx(0))
            painter.drawLine(px, 0, px, self.height())

        painter.setPen(QColor(100, 100, 100))

        x = math.floor(xmin / step) * step
        while x <= xmax:
            if abs(x) > EPS:
                px = round(tx(x))
                py = round(ty(0)) + 15 if ymin <= 0 <= ymax else self.height() - 5
                painter.drawText(px + 3, min(py, self.height() - 3), f"{x:g}")
            x += step

        y = math.floor(ymin / step) * step
        while y <= ymax:
            if abs(y) > EPS:
                py = round(ty(y))
                px = round(tx(0)) + 5 if xmin <= 0 <= xmax else 5
                painter.drawText(min(px, self.width() - 30), py - 3, f"{y:g}")
            y += step

    def _draw_source(self, painter, tx, ty):
        pen = QPen(QColor(70, 70, 70), 1.5, Qt.DashLine)
        painter.setPen(pen)

        for x1, y1, x2, y2 in self.segments:
            painter.drawLine(
                QPointF(tx(x1), ty(y1)),
                QPointF(tx(x2), ty(y2)),
            )

    def _draw_rectangle(self, painter, tx, ty):
        if not self.clip_rect:
            return

        xmin, ymin, xmax, ymax = self.clip_rect

        pen = QPen(QColor(220, 0, 0), 2)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)

        rect = QRectF(
            QPointF(tx(xmin), ty(ymax)),
            QPointF(tx(xmax), ty(ymin)),
        )
        painter.drawRect(rect)

    def _draw_polygon(self, painter, tx, ty):
        if not self.polygon:
            return

        pen = QPen(QColor(0, 0, 200), 2)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)

        points = [
            QPointF(tx(x), ty(y))
            for x, y in self.polygon
        ]

        for i in range(len(points)):
            painter.drawLine(
                points[i],
                points[(i + 1) % len(points)],
            )

    def _draw_rectangle_result(self, painter, tx, ty):
        if not self.clip_rect:
            return

        pen = QPen(QColor(0, 150, 0), 3)
        painter.setPen(pen)

        for segment in self.segments:
            result = clipper.liang_barsky(
                *segment,
                *self.clip_rect,
            )

            if result is None:
                continue

            x1, y1, x2, y2 = result
            painter.drawLine(
                QPointF(tx(x1), ty(y1)),
                QPointF(tx(x2), ty(y2)),
            )

    def _draw_polygon_result(self, painter, tx, ty):
        if not self.polygon:
            return

        pen = QPen(QColor(230, 110, 0), 3)
        painter.setPen(pen)

        for segment in self.segments:
            result = clipper.clip_segment_by_convex_polygon(
                *segment,
                self.polygon,
            )

            if result is None:
                continue

            x1, y1, x2, y2 = result
            painter.drawLine(
                QPointF(tx(x1), ty(y1)),
                QPointF(tx(x2), ty(y2)),
            )


EPS = 1e-9


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Отсечение отрезков")
        self.resize(1100, 800)

        central = QWidget()
        layout = QVBoxLayout(central)

        buttons = QHBoxLayout()

        self.default_button = QPushButton("Дефолтные данные")
        self.default_button.clicked.connect(self.load_default)

        self.file_button = QPushButton("Загрузить из файла")
        self.file_button.clicked.connect(self.load_file)

        buttons.addWidget(self.default_button)
        buttons.addWidget(self.file_button)
        buttons.addStretch()

        layout.addLayout(buttons)

        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Режим работы:"))

        self.mode = QComboBox()
        self.mode.addItem("Лианг - Барски", "rectangle")
        self.mode.addItem("Отсечение выпуклым многоугольником", "polygon")
        self.mode.addItem("Сравнение алгоритмов", "both")
        self.mode.currentIndexChanged.connect(self.change_mode)

        mode_layout.addWidget(self.mode)
        mode_layout.addStretch()

        layout.addLayout(mode_layout)

        self.canvas = Canvas()
        layout.addWidget(self.canvas, 1)

        layout.addWidget(QLabel("Обозначения:"))

        legend = QHBoxLayout()
        legend.addWidget(self.legend_item("#464646", "Исходные отрезки"))
        legend.addWidget(self.legend_item("#dc0000", "Прямоугольное окно"))
        legend.addWidget(self.legend_item("#0000c8", "Выпуклый многоугольник"))
        legend.addWidget(self.legend_item("#009600", "Результат Лианга - Барски"))
        legend.addWidget(self.legend_item("#e66e00", "Результат отсечения многоугольником"))
        legend.addStretch()

        layout.addLayout(legend)

        self.setCentralWidget(central)
        self.load_default()

    def legend_item(self, color, text):
        label = QLabel(f"■ {text}")
        label.setStyleSheet(f"color: {color};")
        return label

    def change_mode(self):
        self.canvas.mode = self.mode.currentData()
        self.canvas.update()

    def update_modes(self):
        model = self.mode.model()
        has_polygon = self.canvas.polygon is not None

        model.item(1).setEnabled(has_polygon)
        model.item(2).setEnabled(has_polygon)

        if not has_polygon:
            self.mode.setCurrentIndex(0)

        self.change_mode()

    def load_default(self):
        self.canvas.set_data(
            list(DEFAULT_SEGMENTS),
            DEFAULT_RECT,
            list(DEFAULT_POLYGON),
        )
        self.update_modes()

    def load_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Открыть файл",
            "",
            "Text files (*.txt);;All files (*)",
        )

        if not path:
            return

        try:
            segments, clip_rect, polygon = clipper.read_input(path)
        except (ValueError, OSError) as error:
            QMessageBox.critical(self, "Ошибка загрузки", str(error))
            return

        self.canvas.set_data(segments, clip_rect, polygon)
        self.update_modes()