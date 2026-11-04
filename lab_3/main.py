import sys
import time
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QComboBox, QLineEdit, QLabel, QFormLayout, QGroupBox,
    QCheckBox
)

from canvas import RasterCanvas
from algorithms import step_by_step, dda, bresenham_line, bresenham_circle


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LR3 - Raster Algorithms")
        self.canvas = RasterCanvas()

        panel = QGroupBox("Params")
        form = QFormLayout()

        self.algo = QComboBox()
        self.algo.addItems([
            "Step-by-step",
            "DDA",
            "Bresenham (line)",
            "Bresenham (circle)",
        ])
        self.algo.currentIndexChanged.connect(self._on_algo_changed)

        self.x1 = QLineEdit("0")
        self.y1 = QLineEdit("0")
        self.x2 = QLineEdit("10")
        self.y2 = QLineEdit("7")
        self.r = QLineEdit("8")

        self.btn_draw = QPushButton("Draw")
        self.btn_draw.clicked.connect(self.draw)

        self.lbl_info = QLabel("Points: -")
        self.lbl_info.setWordWrap(True)

        self.chk_centers = QCheckBox("Show centers")
        self.chk_centers.toggled.connect(self._toggle_centers)

        form.addRow("Algorithm:", self.algo)
        form.addRow("x1:", self.x1)
        form.addRow("y1:", self.y1)
        form.addRow("x2:", self.x2)
        form.addRow("y2:", self.y2)
        form.addRow("R:", self.r)
        form.addRow(self.btn_draw)
        form.addRow(self.lbl_info)
        form.addRow(self.chk_centers)

        zoom_box = QHBoxLayout()
        btn_in = QPushButton("+")
        btn_out = QPushButton("-")
        btn_in.clicked.connect(lambda: self.canvas.zoom(1.25))
        btn_out.clicked.connect(lambda: self.canvas.zoom(0.8))
        zoom_box.addWidget(QLabel("Zoom:"))
        zoom_box.addWidget(btn_in)
        zoom_box.addWidget(btn_out)
        form.addRow(zoom_box)

        panel.setLayout(form)
        panel.setFixedWidth(260)

        central = QWidget()
        lay = QHBoxLayout(central)
        lay.addWidget(self.canvas, 1)
        lay.addWidget(panel)
        self.setCentralWidget(central)
        self.resize(1100, 750)

        self._on_algo_changed()

    def _on_algo_changed(self):
        is_circle = self.algo.currentIndex() == 3
        self.x2.setEnabled(not is_circle)
        self.y2.setEnabled(not is_circle)
        self.r.setEnabled(is_circle)

    def _toggle_centers(self, checked):
        self.canvas.show_centers = checked
        self.canvas.update()

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
            "Points: " + str(len(pts)) + "\n"
            + "Time: " + str(round((t1 - t0) * 1e6, 1)) + " us"
        )
        self.canvas.set_points(pts)


def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
