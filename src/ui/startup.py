from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt

class StartupWidget(QWidget):
    def __init__(self, on_select_unit):
        super().__init__()
        self.on_select_unit = on_select_unit
        layout = QVBoxLayout()
        title = QLabel("MathTeach")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20pt; font-weight: bold;")
        subtitle = QLabel("Select a Unit to begin")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("font-size: 10pt;")
        layout.addWidget(title)
        layout.addWidget(subtitle)
        buttons_layout = QHBoxLayout()
        units = [("Algebra","algebra"),("Trigonometry","trigonometry"),("Geometry","geometry"),("Calculus","calculus")]
        for name, key in units:
            btn = QPushButton(name)
            btn.setMinimumHeight(40)
            btn.clicked.connect(lambda checked, k=key: self.on_select_unit(k))
            buttons_layout.addWidget(btn)
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
