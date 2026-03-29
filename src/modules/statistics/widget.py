from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit
import math

class StatisticsWidget(QWidget):
    def __init__(self):
        super().__init__()
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        self.setWindowTitle('Statistics Module')

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText('Enter values comma-separated, e.g. 4, 10, 15, 7')
        main_layout.addWidget(self.input_field)

        btn_layout = QHBoxLayout()
        self.mean_btn = QPushButton('Mean')
        self.median_btn = QPushButton('Median')
        self.mode_btn = QPushButton('Mode')
        self.std_btn = QPushButton('StdDev')

        self.mean_btn.clicked.connect(lambda: self.calculate('mean'))
        self.median_btn.clicked.connect(lambda: self.calculate('median'))
        self.mode_btn.clicked.connect(lambda: self.calculate('mode'))
        self.std_btn.clicked.connect(lambda: self.calculate('std'))

        btn_layout.addWidget(self.mean_btn)
        btn_layout.addWidget(self.median_btn)
        btn_layout.addWidget(self.mode_btn)
        btn_layout.addWidget(self.std_btn)
        main_layout.addLayout(btn_layout)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        main_layout.addWidget(self.output)

    def _values(self):
        try:
            return [float(v.strip()) for v in self.input_field.text().split(',') if v.strip()]
        except Exception:
            return []

    def calculate(self, mode):
        vals = self._values()
        if not vals:
            self.output.setPlainText('No valid numeric input')
            return

        if mode == 'mean':
            m = sum(vals) / len(vals)
            self.output.setPlainText(f'Mean = {m:.4f}')
        elif mode == 'median':
            s = sorted(vals)
            n = len(s)
            med = s[n//2] if n % 2 == 1 else (s[n//2-1] + s[n//2]) / 2
            self.output.setPlainText(f'Median = {med:.4f}')
        elif mode == 'mode':
            mode_value = max(set(vals), key=vals.count)
            self.output.setPlainText(f'Mode = {mode_value:.4f}')
        elif mode == 'std':
            m = sum(vals) / len(vals)
            var = sum((x - m)**2 for x in vals)/len(vals)
            sd = math.sqrt(var)
            self.output.setPlainText(f'StdDev = {sd:.4f}')
