from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QComboBox, QHBoxLayout
from PySide6.QtCore import Qt
from src.engine.math_engine import MathEngine

class ProbabilityWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.engine = MathEngine()

        layout = QVBoxLayout()
        header = QLabel('Probability Distributions')
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet('font-size: 14pt; font-weight: bold;')
        layout.addWidget(header)

        self.dist_combo = QComboBox()
        self.dist_combo.addItems(['Binomial', 'Normal'])
        layout.addWidget(self.dist_combo)

        self.params_input = QLineEdit()
        self.params_input.setPlaceholderText('Binomial: n,k,p  |  Normal: x,mu,sigma')
        layout.addWidget(self.params_input)

        btn_layout = QHBoxLayout()
        self.calc_btn = QPushButton('Calculate')
        self.calc_cdf_btn = QPushButton('CDF')
        self.calc_btn.clicked.connect(self.calc_pdf)
        self.calc_cdf_btn.clicked.connect(self.calc_cdf)
        btn_layout.addWidget(self.calc_btn)
        btn_layout.addWidget(self.calc_cdf_btn)
        layout.addLayout(btn_layout)

        self.result_box = QTextEdit()
        self.result_box.setReadOnly(True)
        layout.addWidget(self.result_box)

        self.setLayout(layout)

    def calc_pdf(self):
        dist = self.dist_combo.currentText()
        parts = [p.strip() for p in self.params_input.text().split(',') if p.strip()]
        try:
            if dist == 'Binomial':
                n, k, p = int(parts[0]), int(parts[1]), float(parts[2])
                val = self.engine.binomial_pmf(n, k, p)
                self.result_box.setPlainText(f'PMF(n={n}, k={k}, p={p}) = {val:.6f}')
            else:
                x, mu, sigma = float(parts[0]), float(parts[1]), float(parts[2])
                val = self.engine.normal_pdf(x, mu, sigma)
                self.result_box.setPlainText(f'PDF(x={x}, μ={mu}, σ={sigma}) = {val:.6f}')
        except Exception as e:
            self.result_box.setPlainText(f'Calculation error: {e}')

    def calc_cdf(self):
        dist = self.dist_combo.currentText()
        parts = [p.strip() for p in self.params_input.text().split(',') if p.strip()]
        try:
            if dist == 'Binomial':
                n, k, p = int(parts[0]), int(parts[1]), float(parts[2])
                val = self.engine.binomial_cdf(n, k, p)
                self.result_box.setPlainText(f'CDF(k<={k}) = {val:.6f}')
            else:
                x, mu, sigma = float(parts[0]), float(parts[1]), float(parts[2])
                val = self.engine.normal_cdf(x, mu, sigma)
                self.result_box.setPlainText(f'CDF(x={x}) = {val:.6f}')
        except Exception as e:
            self.result_box.setPlainText(f'Calculation error: {e}')
