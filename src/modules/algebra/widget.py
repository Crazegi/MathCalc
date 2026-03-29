from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QCheckBox, QTextEdit, QLabel
import pyqtgraph as pg
import numpy as np
from src.engine.math_engine import MathEngine

class AlgebraWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.engine = MathEngine()
        main_layout = QVBoxLayout()
        top_layout = QHBoxLayout()
        self.input_line = QLineEdit()
        self.input_line.setPlaceholderText("Enter expression or equation (e.g. x^2+2*x+1, or x^2 = 4)")
        self.calc_button = QPushButton("Calculate")
        self.calc_button.clicked.connect(self.on_calculate)
        self.show_steps_cb = QCheckBox("Show steps")
        top_layout.addWidget(self.input_line)
        top_layout.addWidget(self.calc_button)
        top_layout.addWidget(self.show_steps_cb)
        main_layout.addLayout(top_layout)
        self.result_label = QLabel("Result: ")
        main_layout.addWidget(self.result_label)
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        main_layout.addWidget(self.plot_widget, stretch=1)
        self.steps_view = QTextEdit()
        self.steps_view.setReadOnly(True)
        self.steps_view.setFixedHeight(180)
        main_layout.addWidget(self.steps_view)
        self.setLayout(main_layout)

    def on_calculate(self):
        expr_text = self.input_line.text().strip()
        if not expr_text:
            return
        steps, result, plot = self.engine.analyze_input(expr_text)
        self.result_label.setText(f"Result: {result}")
        if self.show_steps_cb.isChecked():
            self.steps_view.setPlainText("\n".join(steps))
        else:
            self.steps_view.clear()
        self.plot_widget.clear()
        if plot is not None:
            x, y = plot
            try:
                y = np.array(y, dtype=float)
                x = np.array(x, dtype=float)
                self.plot_widget.plot(x, y, pen=pg.mkPen('b', width=2))
            except Exception as e:
                self.steps_view.append(f"\n[Plotting error]: {e}")
