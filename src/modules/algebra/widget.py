from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QCheckBox, QTextEdit, QLabel
import pyqtgraph as pg
import numpy as np
import sympy as sp
from src.engine.math_engine import MathEngine

class AlgebraWidget(QWidget):
    def __init__(self, geometry_callback=None):
        super().__init__()
        self.engine = MathEngine()
        self.geometry_callback = geometry_callback
        main_layout = QVBoxLayout()
        top_layout = QHBoxLayout()
        self.input_line = QLineEdit()
        self.input_line.setPlaceholderText("Enter expression or equation (e.g. x^2+2*x+1, or x^2 = 4)")
        self.calc_button = QPushButton("Calculate")
        self.calc_button.clicked.connect(self.on_calculate)
        self.apply_geo_button = QPushButton("Apply to Geometry")
        self.apply_geo_button.clicked.connect(self.on_apply_geometry)
        self.show_steps_cb = QCheckBox("Show steps")
        top_layout.addWidget(self.input_line)
        top_layout.addWidget(self.calc_button)
        top_layout.addWidget(self.apply_geo_button)
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

    def on_apply_geometry(self):
        expr_text = self.input_line.text().strip()
        if not expr_text:
            return
        msg = self.apply_equation(expr_text)
        self.steps_view.append(f'Geometry: {msg}')

    def apply_equation(self, eq_text: str) -> str:
        try:
            if self.geometry_callback is None:
                return 'No geometry callback attached.'
            eq = sp.sympify(eq_text.replace('^', '**'))
            if isinstance(eq, sp.Equality):
                lhs = eq.lhs
                rhs = eq.rhs
            else:
                # assume equation like y - 2*x - 1
                lhs = eq
                rhs = 0

            x, y = sp.symbols('x y')
            solve_y = sp.solve(sp.Eq(lhs, rhs), y)
            if solve_y:
                m_expr = solve_y[0]
                # line y=m*x+b
                if m_expr.has(x):
                    m = float(sp.simplify(sp.diff(m_expr, x))) if m_expr.has(x) else 0.0
                    b = float(m_expr.subs(x, 0))
                    return self.geometry_callback(f'line:{m}:{b}')
            solve_x = sp.solve(sp.Eq(lhs, rhs), x)
            if solve_x:
                val = solve_x[0]
                if not val.has(y):
                    return self.geometry_callback(f'vertical:{float(val)}')

            # circle detection for e.g. (x-2)**2 + (y-3)**2 = 25
            expr = sp.simplify(lhs - rhs)
            xp2 = sp.expand(expr)
            if xp2.has(x**2) and xp2.has(y**2):
                A = xp2.coeff(x,2)
                B = xp2.coeff(y,2)
                if A == 1 and B == 1:
                    Dx = xp2.coeff(x,1)
                    Ey = xp2.coeff(y,1)
                    F = xp2.subs({x:0, y:0})
                    cx = -Dx/2
                    cy = -Ey/2
                    r = sp.sqrt(cx**2 + cy**2 - F)
                    return self.geometry_callback(f'circle:{float(cx)}:{float(cy)}:{float(r)}')

            return 'Expression not recognized for geometry injection.'
        except Exception as e:
            return f'Geometry parsing error: {e}'
