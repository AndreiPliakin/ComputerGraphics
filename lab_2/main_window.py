import os

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt

from image_utils import (
    IMAGES_DIR, list_image_files, load_image_gray, np_to_qpixmap,
)
from threshold_methods import otsu_threshold, iterative_threshold
from sharpen_methods import laplacian_sharpen, unsharp_mask


class ImageLabel(QtWidgets.QWidget):
    def __init__(self, title: str):
        super().__init__()
        self.title = QtWidgets.QLabel(title)
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("font-weight: bold;")

        self.image = QtWidgets.QLabel("—")
        self.image.setAlignment(Qt.AlignCenter)
        self.image.setMinimumSize(340, 340)
        self.image.setStyleSheet("border: 1px solid gray; background: #fafafa;")

        self.caption = QtWidgets.QLabel("")
        self.caption.setAlignment(Qt.AlignCenter)
        self.caption.setStyleSheet("color: #555;")

        lay = QtWidgets.QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.title)
        lay.addWidget(self.image, 1)
        lay.addWidget(self.caption)

    def set_pixmap(self, img, max_size: int = 340):
        self.image.setPixmap(np_to_qpixmap(img, max_size))
        self.image.setText("")

    def clear(self):
        self.image.clear()
        self.image.setText("—")
        self.caption.setText("")


class ParamSlider(QtWidgets.QWidget):
    def __init__(self, name: str, low: int, high: int, value: int, scale: float):
        super().__init__()
        self.scale = scale
        self.slider = QtWidgets.QSlider(Qt.Horizontal)
        self.slider.setRange(low, high)
        self.slider.setValue(value)
        self.label = QtWidgets.QLabel(name)
        self.label.setMinimumWidth(60)
        self.value_label = QtWidgets.QLabel(f"{value * scale:.2f}")
        self.value_label.setMinimumWidth(50)
        self.slider.valueChanged.connect(self._on_changed)

        lay = QtWidgets.QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.label)
        lay.addWidget(self.slider, 1)
        lay.addWidget(self.value_label)

    def _on_changed(self, v: int):
        self.value_label.setText(f"{v * self.scale:.2f}")

    def value(self) -> float:
        return self.slider.value() * self.scale

    def connect(self, fn):
        self.slider.valueChanged.connect(fn)


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.gray = None
        self.params_a = []
        self.params_b = []

        self.setWindowTitle("Лаб 2: порог / резкость")
        self.resize(1000, 1000)
        self._build_ui()
        self._autoload_first()

    def _build_ui(self):
        self.combo_file = QtWidgets.QComboBox()
        self.combo_file.setMinimumWidth(340)
        self._refresh_file_list()
        self.combo_file.currentIndexChanged.connect(self._on_file_changed)

        self.rb_pair_thr = QtWidgets.QRadioButton("Порог: Оцу vs Итеративный")
        self.rb_pair_shp = QtWidgets.QRadioButton("Резкость: Лаплас vs Unsharp")
        self.rb_pair_thr.setChecked(True)
        self.rb_pair_thr.toggled.connect(self._on_pair_changed)

        row_file = QtWidgets.QHBoxLayout()
        row_file.addWidget(QtWidgets.QLabel("Файл:"))
        row_file.addWidget(self.combo_file, 1)

        row_pair = QtWidgets.QHBoxLayout()
        row_pair.addWidget(QtWidgets.QLabel("Пара методов:"))
        row_pair.addWidget(self.rb_pair_thr)
        row_pair.addWidget(self.rb_pair_shp)
        row_pair.addStretch(1)

        self.lbl_src_a = ImageLabel("Исходное")
        self.lbl_res_a = ImageLabel("Метод A")

        self.lbl_src_b = ImageLabel("Исходное")
        self.lbl_res_b = ImageLabel("Метод B")

        row_a = QtWidgets.QHBoxLayout()
        row_a.addWidget(self.lbl_src_a)
        row_a.addWidget(self.lbl_res_a)

        row_b = QtWidgets.QHBoxLayout()
        row_b.addWidget(self.lbl_src_b)
        row_b.addWidget(self.lbl_res_b)

        self.params_a_container = QtWidgets.QWidget()
        self.params_a_layout = QtWidgets.QHBoxLayout(self.params_a_container)
        self.params_a_layout.setContentsMargins(0, 0, 0, 0)

        self.params_b_container = QtWidgets.QWidget()
        self.params_b_layout = QtWidgets.QHBoxLayout(self.params_b_container)
        self.params_b_layout.setContentsMargins(0, 0, 0, 0)

        main = QtWidgets.QVBoxLayout(self)
        main.addLayout(row_file)
        main.addLayout(row_pair)
        main.addLayout(row_a, 1)
        main.addWidget(self.params_a_container)
        main.addLayout(row_b, 1)
        main.addWidget(self.params_b_container)

        self._on_pair_changed()

    def _refresh_file_list(self):
        current = self.combo_file.currentText()
        self.combo_file.blockSignals(True)
        self.combo_file.clear()
        files = list_image_files()
        self.combo_file.addItems(files)
        if current in files:
            self.combo_file.setCurrentText(current)
        self.combo_file.blockSignals(False)

    def _autoload_first(self):
        if self.combo_file.count() > 0:
            self._on_file_changed()

    def _on_file_changed(self):
        name = self.combo_file.currentText()
        if not name:
            self.gray = None
            self._clear_images()
            return
        path = os.path.join(IMAGES_DIR, name)
        gray = load_image_gray(path)
        if gray is None:
            self.gray = None
            self._clear_images()
            return
        self.gray = gray
        for lbl in (self.lbl_src_a, self.lbl_src_b):
            lbl.set_pixmap(gray)
            lbl.caption.setText(f"{name}  {gray.shape[1]}×{gray.shape[0]}")
        self._recompute()

    def _clear_images(self):
        for lbl in (self.lbl_src_a, self.lbl_res_a,
                    self.lbl_src_b, self.lbl_res_b):
            lbl.clear()

    def _clear_params(self):
        for w in self.params_a + self.params_b:
            w.setParent(None)
        self.params_a = []
        self.params_b = []

    def _add_param(self, layout, container_list, widget):
        container_list.append(widget)
        layout.addWidget(widget)
        widget.connect(lambda _v: self._recompute())

    def _on_pair_changed(self):
        self._clear_params()

        if self.rb_pair_thr.isChecked():
            self.lbl_res_a.title.setText("Результат: Оцу")
            self.lbl_res_b.title.setText("Результат: итеративный")
        else:
            self.lbl_res_a.title.setText("Результат: Лаплас")
            self.lbl_res_b.title.setText("Результат: Unsharp Mask")
            self._add_param(
                self.params_a_layout, self.params_a,
                ParamSlider("gain", 0, 200, 100, 0.01),
            )
            self._add_param(
                self.params_b_layout, self.params_b,
                ParamSlider("sigma", 1, 100, 30, 0.1),
            )
            self._add_param(
                self.params_b_layout, self.params_b,
                ParamSlider("k", 0, 300, 100, 0.01),
            )

        if self.gray is not None:
            self._recompute()

    def _get(self, container_list, name, default):
        for w in container_list:
            if w.label.text() == name:
                return w.value()
        return default

    def _recompute(self):
        if self.gray is None:
            return

        if self.rb_pair_thr.isChecked():
            res_a, t_a = otsu_threshold(self.gray)
            self.lbl_res_a.set_pixmap(res_a)
            self.lbl_res_a.caption.setText(f"порог = {t_a}")

            eps = self._get(self.params_b, "eps", 1.0)
            res_b, t_b = iterative_threshold(self.gray, eps=eps)
            self.lbl_res_b.set_pixmap(res_b)
            self.lbl_res_b.caption.setText(f"порог = {t_b:.2f}, eps = {eps:.1f}")
        else:
            gain = self._get(self.params_a, "gain", 1.0)
            res_a = laplacian_sharpen(self.gray, gain=gain)
            self.lbl_res_a.set_pixmap(res_a)
            self.lbl_res_a.caption.setText(f"gain = {gain:.2f}")

            sigma = self._get(self.params_b, "sigma", 3.0)
            k = self._get(self.params_b, "k", 1.0)
            res_b = unsharp_mask(self.gray, sigma=sigma, k=k)
            self.lbl_res_b.set_pixmap(res_b)
            self.lbl_res_b.caption.setText(f"sigma = {sigma:.2f}, k = {k:.2f}")


def main():
    import sys
    from PyQt5 import QtWidgets as QW
    app = QW.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())