from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QComboBox
from PySide6.QtCore import Qt
from src.engine.math_engine import MathEngine

class TrigonometryWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.engine = MathEngine()

        layout = QVBoxLayout()
        title = QLabel("Trigonometry Module")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 16pt; font-weight: bold;")
        layout.addWidget(title)

        input_layout = QHBoxLayout()
        self.expr_input = QLineEdit()
        self.expr_input.setPlaceholderText("Enter trig expression, e.g. sin(x)+cos(x)")
        self.eval_point = QLineEdit()
        self.eval_point.setPlaceholderText("x value (e.g. 30 or pi/6)")
        self.unit_combo = QComboBox()
        self.unit_combo.addItems(["deg", "rad"])
        input_layout.addWidget(self.expr_input)
        input_layout.addWidget(self.eval_point)
        input_layout.addWidget(self.unit_combo)

        layout.addLayout(input_layout)

        btn_layout = QHBoxLayout()
        self.eval_btn = QPushButton("Evaluate")
        self.eval_btn.clicked.connect(self.on_evaluate)
        self.simplify_btn = QPushButton("Simplify Identity")
        self.simplify_btn.clicked.connect(self.on_simplify)
        self.verify_btn = QPushButton("Verify Identity")
        self.verify_btn.clicked.connect(self.on_verify)
        btn_layout.addWidget(self.eval_btn)
        btn_layout.addWidget(self.simplify_btn)
        btn_layout.addWidget(self.verify_btn)
        layout.addLayout(btn_layout)

        self.result_label = QLabel("Result: ")
        layout.addWidget(self.result_label)

        self.steps_text = QTextEdit()
        self.steps_text.setReadOnly(True)
        self.steps_text.setFixedHeight(170)
        layout.addWidget(self.steps_text)

        self.setLayout(layout)

    def on_evaluate(self):
        expr = self.expr_input.text().strip()
        point = self.eval_point.text().strip() or None
        unit = self.unit_combo.currentText()
        if not expr:
            return
        try:
            val, steps = self.engine.evaluate_trig(expr, value=point, unit=unit)
            self.result_label.setText(f"Result: {val}")
            self.steps_text.setPlainText('\n'.join(steps))
        except Exception as e:
            self.result_label.setText(f"Error: {e}")
            self.steps_text.setPlainText('')

    def on_simplify(self):
        expr = self.expr_input.text().strip()
        if not expr:
            return
        try:
            simplified, steps = self.engine.simplify_trig(expr)
            self.result_label.setText(f"Simplified: {simplified}")
            self.steps_text.setPlainText('\n'.join(steps))
        except Exception as e:
            self.result_label.setText(f"Error: {e}")
            self.steps_text.setPlainText('')

    def on_verify(self):
        text = self.expr_input.text().strip()
        if '=' not in text:
            self.result_label.setText("Enter identity as A=B")
            return
        a, b = [p.strip() for p in text.split('=', 1)]
        try:
            valid, steps = self.engine.verify_trig_identity(a, b)
            self.result_label.setText("Identity True" if valid else "Identity False")
            self.steps_text.setPlainText('\n'.join(steps))
        except Exception as e:
            self.result_label.setText(f"Error: {e}")
            self.steps_text.setPlainText('')
