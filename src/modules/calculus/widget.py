from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QTextEdit
import pyqtgraph as pg
import numpy as np
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
from PySide6.QtGui import QFont


class CalculusWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.transformations = (standard_transformations + (implicit_multiplication_application,))
        self.func = None

        self.expr_input = QLineEdit()
        self.expr_input.setPlaceholderText('f(x) expression, e.g. x**3 + 2*x - 5')

        self.point_input = QLineEdit()
        self.point_input.setPlaceholderText('Point value for derivative/limit/area, e.g. 2 or [1,3]')

        self.diff_btn = QPushButton('Derivative')
        self.int_btn = QPushButton('Integral')
        self.limit_btn = QPushButton('Limit')
        self.series_btn = QPushButton('Series')

        self.diff_btn.clicked.connect(self.do_derivative)
        self.int_btn.clicked.connect(self.do_integral)
        self.limit_btn.clicked.connect(self.do_limit)
        self.series_btn.clicked.connect(self.do_series)

        self.graph = pg.PlotWidget()
        self.graph.setBackground('w')

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setFont(QFont('Courier', 10))

        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel('f(x):'))
        top_layout.addWidget(self.expr_input)
        top_layout.addWidget(QLabel('x or [a,b]:'))
        top_layout.addWidget(self.point_input)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.diff_btn)
        button_layout.addWidget(self.int_btn)
        button_layout.addWidget(self.limit_btn)
        button_layout.addWidget(self.series_btn)

        layout = QVBoxLayout()
        layout.addLayout(top_layout)
        layout.addLayout(button_layout)
        layout.addWidget(QLabel('Graph'))
        layout.addWidget(self.graph, stretch=1)
        layout.addWidget(QLabel('Output / Steps'))
        layout.addWidget(self.output)

        self.setLayout(layout)

    def parse_function(self):
        s = self.expr_input.text().strip()
        if not s:
            raise ValueError('Function expression required')
        s = s.replace('^', '**')
        return parse_expr(s, transformations=self.transformations)

    def plot_function(self, expr):
        x = sp.symbols('x')
        f = sp.lambdify(x, expr, 'numpy')
        xs = np.linspace(-10, 10, 500)
        ys = f(xs)
        self.graph.clear()
        self.graph.plot(xs, ys, pen=pg.mkPen('blue', width=2))

    def do_derivative(self):
        try:
            expr = self.parse_function()
            x = sp.symbols('x')
            first = sp.diff(expr, x)
            second = sp.diff(first, x)
            self.output.setPlainText(f'f(x) = {sp.pretty(expr)}\n')
            self.output.append(f"f'(x) = {sp.pretty(first)}")
            self.output.append(f"f''(x) = {sp.pretty(second)}")
            val = self.point_input.text().strip()
            if val:
                xv = float(val)
                self.output.append(f"f'({xv}) = {float(first.subs(x, xv))}")
            self.plot_function(expr)
        except Exception as e:
            self.output.setPlainText(f'Error: {e}')

    def do_integral(self):
        try:
            expr = self.parse_function()
            x = sp.symbols('x')
            ind = sp.integrate(expr, x)
            self.output.setPlainText(f'f(x) = {sp.pretty(expr)}\n')
            self.output.append(f"∫f(x)dx = {sp.pretty(ind)} + C")
            val = self.point_input.text().strip()
            if val.startswith('[') and val.endswith(']'):
                a,b = [float(v.strip()) for v in val[1:-1].split(',')]
                definite = sp.integrate(expr, (x, a, b))
                self.output.append(f"Definite integral [{a},{b}] = {float(definite)}")
            self.plot_function(expr)
        except Exception as e:
            self.output.setPlainText(f'Error: {e}')

    def do_limit(self):
        try:
            expr = self.parse_function()
            x = sp.symbols('x')
            val = self.point_input.text().strip()
            if not val:
                raise ValueError('Enter point for limit')
            a = float(val)
            lim = sp.limit(expr, x, a)
            self.output.setPlainText(f'lim_(x->{a}) {sp.pretty(expr)} = {sp.pretty(lim)}')
            self.plot_function(expr)
        except Exception as e:
            self.output.setPlainText(f'Error: {e}')

    def do_series(self):
        try:
            expr = self.parse_function()
            x = sp.symbols('x')
            ser = sp.series(expr, x, 0, 6)
            self.output.setPlainText(f'Series expansion around 0:\n{sp.pretty(ser)}')
            self.plot_function(expr)
        except Exception as e:
            self.output.setPlainText(f'Error: {e}')
