from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QHBoxLayout
from PySide6.QtCore import Qt
from src.engine.math_engine import MathEngine

class FunctionsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.engine = MathEngine()

        layout = QVBoxLayout()
        header = QLabel('Functions & Quadratic Analysis')
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet('font-size: 14pt; font-weight: bold;')
        layout.addWidget(header)

        input_layout = QHBoxLayout()
        self.formula_input = QLineEdit()
        self.formula_input.setPlaceholderText('Enter quadratic formula, e.g. x**2 - 4*x + 3')
        self.analyze_btn = QPushButton('Analyze')
        self.analyze_btn.clicked.connect(self.on_analyze)
        input_layout.addWidget(self.formula_input)
        input_layout.addWidget(self.analyze_btn)

        layout.addLayout(input_layout)

        self.result_box = QTextEdit()
        self.result_box.setReadOnly(True)
        layout.addWidget(self.result_box)

        self.plot_btn = QPushButton('Show Vertex Form')
        self.plot_btn.clicked.connect(self.on_vertex)
        layout.addWidget(self.plot_btn)

        self.setLayout(layout)

    def on_analyze(self):
        formula = self.formula_input.text().strip()
        if not formula:
            return
        try:
            props = self.engine.quadratic_properties(formula)
            lines = [f"a={props['a']}, b={props['b']}, c={props['c']}", f"Vertex={props['vertex']}", f"Discriminant={props['discriminant']}", f"Roots={props['roots']}", f"Parabola opens {props['parabola']}."]
            self.result_box.setPlainText('\n'.join(lines))
        except Exception as e:
            self.result_box.setPlainText(f'Analysis error: {e}')

    def on_vertex(self):
        formula = self.formula_input.text().strip()
        if not formula:
            return
        try:
            props = self.engine.quadratic_properties(formula)
            a, b, c = props['a'], props['b'], props['c']
            h, k = props['vertex']
            self.result_box.setPlainText(f"Vertex form: y = {a}*(x - {h})**2 + {k}")
        except Exception as e:
            self.result_box.setPlainText(f'Error computing vertex form: {e}')
