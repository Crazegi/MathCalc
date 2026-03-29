from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QHBoxLayout
from PySide6.QtCore import Qt
from src.engine.math_engine import MathEngine
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import json

class RegressionWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.engine = MathEngine()

        layout = QVBoxLayout()
        header = QLabel('Linear Regression (Least Squares)')
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet('font-size: 14pt; font-weight: bold;')
        layout.addWidget(header)

        self.points_input = QLineEdit()
        self.points_input.setPlaceholderText('Enter points as [(x1,y1), (x2,y2), ...]')
        layout.addWidget(self.points_input)

        btn_layout = QHBoxLayout()
        self.fit_btn = QPushButton('Fit Line')
        self.fit_btn.clicked.connect(self.on_fit)
        self.sim_btn = QPushButton('Monte Carlo Coin')
        self.sim_btn.clicked.connect(self.on_mc)
        btn_layout.addWidget(self.fit_btn)
        btn_layout.addWidget(self.sim_btn)
        self.plot_btn = QPushButton('Plot Regression')
        self.plot_btn.clicked.connect(self.on_plot)
        btn_layout.addWidget(self.plot_btn)
        layout.addLayout(btn_layout)

        self.result_box = QTextEdit()
        self.result_box.setReadOnly(True)
        layout.addWidget(self.result_box)

        self.graph_widget = pg.PlotWidget()
        self.graph_widget.setBackground('w')
        self.graph_widget.setTitle('Regression Scatter + Fit Line')
        self.graph_widget.showGrid(x=True, y=True)
        layout.addWidget(self.graph_widget, stretch=1)

        self.gl_view = gl.GLViewWidget()
        self.gl_view.setCameraPosition(distance=40)
        layout.addWidget(self.gl_view, stretch=1)

        self.scatter_3d = gl.GLScatterPlotItem(size=5, color=(1, 0, 0, 1), pxMode=False)
        self.gl_view.addItem(self.scatter_3d)

        self.setLayout(layout)

    def on_fit(self):
        raw = self.points_input.text().strip()
        try:
            points = json.loads(raw.replace("'", '"'))
            if not isinstance(points, list):
                raise ValueError('Expected list of points')
            props = self.engine.linear_regression(points)
            self.result_box.setPlainText(f"Slope = {props['slope']:.4f}\nIntercept = {props['intercept']:.4f}\nLine: y = {props['slope']:.4f}x + {props['intercept']:.4f}")
        except Exception as e:
            self.result_box.setPlainText(f'Fit error: {e}')

    def on_mc(self):
        try:
            import random
            rate = self.engine.monte_carlo_probability(lambda: random.random() < 0.5, trials=10000)
            self.result_box.setPlainText(f'Monte Carlo estimate for fair coin heads: {rate:.4f}')
        except Exception as e:
            self.result_box.setPlainText(f'MC error: {e}')

    def on_plot(self):
        raw = self.points_input.text().strip()
        try:
            points = json.loads(raw.replace("'", '"'))
            if not isinstance(points, list):
                raise ValueError('Expected list of points')
            props = self.engine.linear_regression(points)
            xs = [float(p[0]) for p in points]
            ys = [float(p[1]) for p in points]
            self.graph_widget.clear()
            self.graph_widget.plot(xs, ys, pen=None, symbol='o', symbolSize=8, symbolBrush='b')
            x_line = [min(xs), max(xs)]
            y_line = [props['slope']*x + props['intercept'] for x in x_line]
            self.graph_widget.plot(x_line, y_line, pen=pg.mkPen('r', width=2))

            # 3D scatter
            z_line = y_line
            xyz = [[x, y, 0] for x, y in zip(xs, ys)]
            self.scatter_3d.setData(pos=xyz, size=5, color=(1,0,0,1))

            self.result_box.setPlainText(f"Plotted {len(points)} points and best-fit line.")
        except Exception as e:
            self.result_box.setPlainText(f'Plot error: {e}')

