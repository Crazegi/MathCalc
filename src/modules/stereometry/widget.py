from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QTextEdit, QHBoxLayout
from PySide6.QtCore import Qt
import math

class StereometryWidget(QWidget):
    def __init__(self):
        super().__init__()

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        main_layout.addWidget(QLabel("Stereometry Module"))

        formula_layout = QHBoxLayout()
        self.solid_combo = QComboBox()
        self.solid_combo.addItems(["Prism", "Pyramid", "Cylinder", "Cone", "Sphere"])
        formula_layout.addWidget(QLabel("Select Solid:"))
        formula_layout.addWidget(self.solid_combo)
        main_layout.addLayout(formula_layout)

        self.param_input = QLineEdit()
        self.param_input.setPlaceholderText("Comma-separated params: e.g. base_area,height or radius,height or radius")
        main_layout.addWidget(self.param_input)

        self.calc_btn = QPushButton("Calculate Volume/Area")
        self.calc_btn.clicked.connect(self.calculate)
        main_layout.addWidget(self.calc_btn)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        main_layout.addWidget(self.output)

    def calculate(self):
        solid = self.solid_combo.currentText()
        args = [p.strip() for p in self.param_input.text().split(',') if p.strip()]
        try:
            if solid == 'Prism':
                base_area = float(args[0])
                h = float(args[1])
                volume = base_area * h
                self.output.setPlainText(f"Prism: V={volume:.4f} (base area*height)")
            elif solid == 'Pyramid':
                base_area = float(args[0])
                h = float(args[1])
                volume = base_area * h / 3
                self.output.setPlainText(f"Pyramid: V={volume:.4f} (1/3*base*height)")
            elif solid == 'Cylinder':
                r = float(args[0])
                h = float(args[1])
                volume = math.pi * r * r * h
                area = 2 * math.pi * r * (r + h)
                self.output.setPlainText(f"Cylinder: V={volume:.4f}, A={area:.4f}")
            elif solid == 'Cone':
                r = float(args[0])
                h = float(args[1])
                volume = math.pi * r * r * h / 3
                self.output.setPlainText(f"Cone: V={volume:.4f}")
            elif solid == 'Sphere':
                r = float(args[0])
                volume = 4/3 * math.pi * r**3
                area = 4 * math.pi * r**2
                self.output.setPlainText(f"Sphere: V={volume:.4f}, A={area:.4f}")
            else:
                self.output.setPlainText("Unknown solid")
        except Exception as e:
            self.output.setPlainText(f"Input error: {e}")
