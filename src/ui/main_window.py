from PySide6.QtWidgets import QMainWindow, QStackedWidget
from src.ui.startup import StartupWidget
from src.modules.algebra.widget import AlgebraWidget
from src.modules.geometry.widget import GeometryWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MathTeach — Math Calculator & Tutor")
        self.stack = QStackedWidget()
        self.startup = StartupWidget(self.show_unit)
        self.algebra = AlgebraWidget(self.apply_geometry_equation)
        self.geometry = GeometryWidget()
        self.stack.addWidget(self.startup)
        self.stack.addWidget(self.algebra)
        self.stack.addWidget(self.geometry)
        self.setCentralWidget(self.stack)
        self.setMinimumSize(800, 600)
        self.stack.setCurrentWidget(self.startup)

    def show_unit(self, unit_name: str):
        if unit_name == 'algebra':
            self.stack.setCurrentWidget(self.algebra)
        elif unit_name == 'geometry':
            self.stack.setCurrentWidget(self.geometry)
        else:
            # other units not implemented yet — return to startup
            self.stack.setCurrentWidget(self.startup)

    def apply_geometry_equation(self, equation: str) -> str:
        # Parse equation from Algebra and apply to geometry unit if available.
        if not hasattr(self, 'geometry') or self.geometry is None:
            return 'Geometry unit not available.'
        return self.geometry.apply_equation(equation)

