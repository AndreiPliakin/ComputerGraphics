import random

from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSlider,
    QDoubleSpinBox,
    QLabel,
    QPushButton
)

from PyQt5.QtCore import Qt

from color_models import RGB, CMYK, HSV
from color_state import ColorState


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Цветовые модели")
        self.setMinimumSize(850, 600)

        self.state = ColorState(RGB(70.0, 130.0, 180.0))
        self.updating = False

        self.create_ui()
        self.update_ui()

    def create_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        self.color_preview = QLabel()
        self.color_preview.setMinimumHeight(120)

        main_layout.addWidget(self.color_preview)

        models_layout = QVBoxLayout()

        models_layout.addWidget(self.create_rgb_panel())
        models_layout.addWidget(self.create_cmyk_panel())
        models_layout.addWidget(self.create_hsv_panel())

        main_layout.addLayout(models_layout)

        main_layout.addLayout(self.create_palette())

    def create_rgb_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)

        self.rgb_controls = []

        components = [
            ("R", "Red (0–255)"),
            ("G", "Green (0–255)"),
            ("B", "Blue (0–255)")
        ]

        for name, description in components:
            slider = QSlider(Qt.Horizontal)
            slider.setRange(0, 255)

            spinbox = QDoubleSpinBox()
            spinbox.setRange(0, 255)
            spinbox.setDecimals(2)
            spinbox.setSingleStep(1)
            spinbox.setFixedWidth(80)

            slider.valueChanged.connect(self.rgb_slider_changed)
            spinbox.valueChanged.connect(self.rgb_spinbox_changed)

            row = QHBoxLayout()
            row.addWidget(QLabel(name))
            row.addWidget(slider)
            row.addWidget(spinbox)

            description_label = QLabel(description)
            description_label.setStyleSheet("color: #666666;")
            row.addWidget(description_label)

            layout.addLayout(row)

            self.rgb_controls.append((slider, spinbox))

        random_button = QPushButton("Random color")
        random_button.clicked.connect(self.random_rgb)
        layout.addWidget(random_button)

        return panel

    def create_cmyk_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)

        self.cmyk_controls = []

        components = [
            ("C", "Cyan (0–1)"),
            ("M", "Magenta (0–1)"),
            ("Y", "Yellow (0–1)"),
            ("K", "Black (0–1)")
        ]

        for name, description in components:
            slider = QSlider(Qt.Horizontal)
            slider.setRange(0, 100)

            spinbox = QDoubleSpinBox()
            spinbox.setRange(0, 1)
            spinbox.setDecimals(4)
            spinbox.setSingleStep(0.01)
            spinbox.setFixedWidth(80)

            slider.valueChanged.connect(self.cmyk_slider_changed)
            spinbox.valueChanged.connect(self.cmyk_spinbox_changed)

            row = QHBoxLayout()
            row.addWidget(QLabel(name))
            row.addWidget(slider)
            row.addWidget(spinbox)

            description_label = QLabel(description)
            description_label.setStyleSheet("color: #666666;")
            row.addWidget(description_label)

            layout.addLayout(row)

            self.cmyk_controls.append((slider, spinbox))

        random_button = QPushButton("Random color")
        random_button.clicked.connect(self.random_cmyk)
        layout.addWidget(random_button)

        return panel

    def create_hsv_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)

        self.hsv_controls = []

        components = [
            ("H", "Hue (0–360°)"),
            ("S", "Saturation (0–1)"),
            ("V", "Value (0–1)")
        ]

        for i, (name, description) in enumerate(components):
            slider = QSlider(Qt.Horizontal)

            spinbox = QDoubleSpinBox()
            spinbox.setFixedWidth(80)

            if i == 0:
                slider.setRange(0, 360)
                spinbox.setRange(0, 360)
                spinbox.setDecimals(2)
                spinbox.setSingleStep(1)
            else:
                slider.setRange(0, 100)
                spinbox.setRange(0, 1)
                spinbox.setDecimals(4)
                spinbox.setSingleStep(0.01)

            slider.valueChanged.connect(self.hsv_slider_changed)
            spinbox.valueChanged.connect(self.hsv_spinbox_changed)

            row = QHBoxLayout()
            row.addWidget(QLabel(name))
            row.addWidget(slider)
            row.addWidget(spinbox)

            description_label = QLabel(description)
            description_label.setStyleSheet("color: #666666;")
            row.addWidget(description_label)

            layout.addLayout(row)

            self.hsv_controls.append((slider, spinbox))

        random_button = QPushButton("Random color")
        random_button.clicked.connect(self.random_hsv)
        layout.addWidget(random_button)

        return panel

    def create_palette(self):
        layout = QHBoxLayout()

        colors = [
            (255, 0, 0),
            (255, 128, 0),
            (255, 255, 0),
            (0, 200, 0),
            (0, 255, 180),
            (0, 180, 255),
            (0, 0, 255),
            (100, 0, 200),
            (255, 0, 180),
            (255, 255, 255),
            (128, 128, 128),
            (0, 0, 0),
            (139, 69, 19),
            (255, 192, 203),
            (128, 0, 0),
            (0, 128, 128),
            (128, 0, 128),
            (255, 215, 0)
        ]

        for r, g, b in colors:
            button = QPushButton()
            button.setFixedSize(40, 40)

            button.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: rgb({r}, {g}, {b});
                    border: 1px solid #777777;
                }}

                QPushButton:hover {{
                    border: 2px solid #333333;
                }}
                """
            )

            button.clicked.connect(
                lambda checked=False, r=r, g=g, b=b:
                self.set_palette_color(r, g, b)
            )

            layout.addWidget(button)

        layout.addStretch()

        return layout

    def set_palette_color(self, r, g, b):
        self.state.set_rgb(RGB(float(r), float(g), float(b)))
        self.update_ui()


    def random_rgb(self):
        rgb = RGB(
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255)
        )

        self.state.set_rgb(rgb)
        self.update_ui()

    def random_cmyk(self):
        cmyk = CMYK(
            random.random(),
            random.random(),
            random.random(),
            random.random()
        )

        self.state.set_cmyk(cmyk)
        self.update_ui()

    def random_hsv(self):
        hsv = HSV(
            random.uniform(0, 360),
            random.random(),
            random.random()
        )

        self.state.set_hsv(hsv)
        self.update_ui()


    def rgb_slider_changed(self):
        if self.updating:
            return

        sender = self.sender()

        for slider, spinbox in self.rgb_controls:
            if slider is sender:
                spinbox.setValue(slider.value())
                break

    def rgb_spinbox_changed(self):
        if self.updating:
            return

        rgb = RGB(
            self.rgb_controls[0][1].value(),
            self.rgb_controls[1][1].value(),
            self.rgb_controls[2][1].value()
        )

        self.state.set_rgb(rgb)
        self.update_ui()


    def cmyk_slider_changed(self):
        if self.updating:
            return

        sender = self.sender()

        for slider, spinbox in self.cmyk_controls:
            if slider is sender:
                spinbox.setValue(slider.value() / 100)
                break

    def cmyk_spinbox_changed(self):
        if self.updating:
            return

        cmyk = CMYK(
            self.cmyk_controls[0][1].value(),
            self.cmyk_controls[1][1].value(),
            self.cmyk_controls[2][1].value(),
            self.cmyk_controls[3][1].value()
        )

        self.state.set_cmyk(cmyk)
        self.update_ui()

    def hsv_slider_changed(self):
        if self.updating:
            return

        sender = self.sender()

        for i, (slider, spinbox) in enumerate(self.hsv_controls):
            if slider is sender:
                if i == 0:
                    spinbox.setValue(slider.value())
                else:
                    spinbox.setValue(slider.value() / 100)
                break

    def hsv_spinbox_changed(self):
        if self.updating:
            return

        hsv = HSV(
            self.hsv_controls[0][1].value(),
            self.hsv_controls[1][1].value(),
            self.hsv_controls[2][1].value()
        )

        self.state.set_hsv(hsv)
        self.update_ui()


    def update_ui(self):
        self.updating = True

        rgb_values = [
            self.state.rgb.r,
            self.state.rgb.g,
            self.state.rgb.b
        ]

        for i, value in enumerate(rgb_values):
            self.rgb_controls[i][0].setValue(round(value))
            self.rgb_controls[i][1].setValue(value)

        cmyk_values = [
            self.state.cmyk.c,
            self.state.cmyk.m,
            self.state.cmyk.y,
            self.state.cmyk.k
        ]

        for i, value in enumerate(cmyk_values):
            self.cmyk_controls[i][0].setValue(round(value * 100))
            self.cmyk_controls[i][1].setValue(value)

        hsv_values = [
            self.state.hsv.h,
            self.state.hsv.s,
            self.state.hsv.v
        ]

        self.hsv_controls[0][0].setValue(round(hsv_values[0]))
        self.hsv_controls[0][1].setValue(hsv_values[0])

        self.hsv_controls[1][0].setValue(round(hsv_values[1] * 100))
        self.hsv_controls[1][1].setValue(hsv_values[1])

        self.hsv_controls[2][0].setValue(round(hsv_values[2] * 100))
        self.hsv_controls[2][1].setValue(hsv_values[2])

        r = round(self.state.rgb.r)
        g = round(self.state.rgb.g)
        b = round(self.state.rgb.b)

        self.color_preview.setStyleSheet(
            f"""
            QLabel {{
                background-color: rgb({r}, {g}, {b});
                border: 1px solid black;
            }}
            """
        )

        slider_style = f"""
            QSlider::groove:horizontal {{
                height: 6px;
                background: #d0d0d0;
                border-radius: 3px;
            }}

            QSlider::sub-page:horizontal {{
                background: #a0a0a0;
                border-radius: 3px;
            }}

            QSlider::add-page:horizontal {{
                background: #d0d0d0;
                border-radius: 3px;
            }}

            QSlider::handle:horizontal {{
                background: rgb({r}, {g}, {b});
                width: 14px;
                margin: -4px 0;
                border-radius: 7px;
                border: 1px solid #666666;
            }}
        """

        for slider, _ in self.rgb_controls:
            slider.setStyleSheet(slider_style)

        for slider, _ in self.cmyk_controls:
            slider.setStyleSheet(slider_style)

        for slider, _ in self.hsv_controls:
            slider.setStyleSheet(slider_style)

        self.updating = False
