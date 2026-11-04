import sys
import time
import math
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QComboBox, QLineEdit, QLabel, QFormLayout, QGroupBox,
    QCheckBox, QSlider
)
from PyQt5.QtCore import Qt

from canvas import RasterCanvas
from algorithms import step_by_step, dda, bresenham_line, bresenham_circle


EXAMPLES = {
    0: ("0", "0", "31", "13", ""),
    1: ("0", "0", "9", "27", ""),
    2: ("-19", "-14", "22", "17", ""),
    3: ("0", "0", "", "", "23"),
}

VISIBLE_MIN = 10
VISIBLE_MAX = 500


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ЛР3 — Базовые растровые алгоритмы")
        self.canvas = RasterCanvas()
        self._user_edited = False

        panel = QGroupBox("Параметры")
        form = QFormLayout()

        self.algo = QComboBox()
        self.algo.addItems([
            "Пошаговый",
            "ЦДА (DDA)",
            "Брезенхем (линия)",
            "Брезенхем (окружность)",
        ])
        self.algo.currentIndexChanged.connect(self._on_algo_changed)

        self.x1 = QLineEdit()
        self.y1 = QLineEdit()
        self.x2 = QLineEdit()
        self.y2 = QLineEdit()
        self.r = QLineEdit()

        for edit in (self.x1, self.y1, self.x2, self.y2, self.r):
            edit.textEdited.connect(self._on_user_edited)

        self.btn_example = QPushButton("Пример")
        self.btn_example.clicked.connect(self.load_example)
        self.btn_draw = QPushButton("Построить")
        self.btn_draw.clicked.connect(self.draw)

        self.lbl_info = QLabel("Точек: —\nВремя: —")
        self.lbl_info.setWordWrap(True)

        self.chk_centers = QCheckBox("Показывать центры")
        self.chk_centers.toggled.connect(self._toggle_centers)

        form.addRow("Алгоритм:", self.algo)
        form.addRow("x1:", self.x1)
        form.addRow("y1:", self.y1)
        form.addRow("x2:", self.x2)
        form.addRow("y2:", self.y2)
        form.addRow("R:", self.r)
        form.addRow(self.btn_example)
        form.addRow(self.btn_draw)
        form.addRow(self.lbl_info)
        form.addRow(self.chk_centers)

        panel.setLayout(form)
        panel.setFixedWidth(260)

        bottom = QWidget()
        bottom_lay = QHBoxLayout(bottom)
        bottom_lay.setContentsMargins(8, 4, 8, 8)

        btn_zoom_out = QPushButton("−")
        btn_zoom_in = QPushButton("+")
        btn_zoom_out.setFixedWidth(40)
        btn_zoom_in.setFixedWidth(40)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(1000)
        self.slider.setInvertedAppearance(True)
        self.slider.valueChanged.connect(self._on_slider)

        btn_zoom_in.clicked.connect(lambda: self._zoom_by(1.25))
        btn_zoom_out.clicked.connect(lambda: self._zoom_by(0.8))

        bottom_lay.addWidget(QLabel("Масштаб:"))
        bottom_lay.addWidget(btn_zoom_in)
        bottom_lay.addWidget(self.slider, 1)
        bottom_lay.addWidget(btn_zoom_out)

        central = QWidget()
        lay = QHBoxLayout(central)
        lay.setContentsMargins(8, 8, 8, 0)
        right = QWidget()
        right_lay = QVBoxLayout(right)
        right_lay.setContentsMargins(0, 0, 0, 0)
        right_lay.addWidget(panel)
        right_lay.addStretch(1)
        lay.addWidget(self.canvas, 1)
        lay.addWidget(right)

        root = QWidget()
        root_lay = QVBoxLayout(root)
        root_lay.setContentsMargins(0, 0, 0, 0)
        root_lay.addWidget(central, 1)
        root_lay.addWidget(bottom)
        self.setCentralWidget(root)

        self.resize(1100, 800)

        self.load_example()
        self.draw()

    def _cell_for_visible(self, n):
        return max(1, int(round(min(self.canvas.width(),
                                    self.canvas.height()) / n)))

    def _cell_max(self):
        return self._cell_for_visible(VISIBLE_MIN)

    def _cell_min(self):
        return self._cell_for_visible(VISIBLE_MAX)

    def _cell_to_slider(self, cell):
        cmin = self._cell_min()
        cmax = self._cell_max()
        if cmax <= cmin:
            return 500
        cell = max(cmin, min(cmax, cell))
        t = math.log(cell / cmin) / math.log(cmax / cmin)
        return int(round(t * 1000))

    def _slider_to_cell(self, t):
        cmin = self._cell_min()
        cmax = self._cell_max()
        if cmax <= cmin:
            return cmin
        return int(round(cmin * (cmax / cmin) ** (t / 1000.0)))

    def _sync_slider(self):
        self.slider.blockSignals(True)
        self.slider.setValue(self._cell_to_slider(self.canvas.cell))
        self.slider.blockSignals(False)

    def _on_slider(self, t):
        self.canvas.set_cell(self._slider_to_cell(t))

    def _zoom_by(self, factor):
        self.canvas.zoom(factor)
        cmin = self._cell_min()
        cmax = self._cell_max()
        if self.canvas.cell < cmin:
            self.canvas.set_cell(cmin)
        if self.canvas.cell > cmax:
            self.canvas.set_cell(cmax)
        self._sync_slider()

    def _on_user_edited(self, text):
        self._user_edited = True

    def _on_algo_changed(self):
        is_circle = self.algo.currentIndex() == 3
        self.x2.setEnabled(not is_circle)
        self.y2.setEnabled(not is_circle)
        self.r.setEnabled(is_circle)
        if not self._user_edited:
            self.load_example()

    def _toggle_centers(self, checked):
        self.canvas.show_centers = checked
        self.canvas.update()

    def load_example(self):
        idx = self.algo.currentIndex()
        x1, y1, x2, y2, r = EXAMPLES[idx]
        for edit, val in zip((self.x1, self.y1, self.x2, self.y2, self.r),
                             (x1, y1, x2, y2, r)):
            edit.blockSignals(True)
            edit.setText(val)
            edit.blockSignals(False)
        self._user_edited = False

    def _safe_int(self, edit, default=0):
        try:
            return int(edit.text().strip())
        except ValueError:
            return default

    def draw(self):
        idx = self.algo.currentIndex()
        x1 = self._safe_int(self.x1)
        y1 = self._safe_int(self.y1)
        x2 = self._safe_int(self.x2)
        y2 = self._safe_int(self.y2)
        r = self._safe_int(self.r, 1)

        t0 = time.perf_counter()
        if idx == 0:
            pts = step_by_step(x1, y1, x2, y2)
        elif idx == 1:
            pts = dda(x1, y1, x2, y2)
        elif idx == 2:
            pts = bresenham_line(x1, y1, x2, y2)
        else:
            pts = bresenham_circle(x1, y1, r)
        t1 = time.perf_counter()

        self.lbl_info.setText(
            f"Точек: {len(pts)}\n"
            f"Время: {(t1 - t0) * 1e6:.1f} мкс"
        )
        self.canvas.set_points(pts)
        self.canvas.fit()
        self._sync_slider()


def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()