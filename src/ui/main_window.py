from PySide6.QtWidgets import QMainWindow, QStackedWidget
from src.ui.startup import StartupWidget
from src.modules.algebra.widget import AlgebraWidget
from src.modules.geometry.widget import GeometryWidget
from src.modules.calculus.widget import CalculusWidget
from src.modules.trigonometry.widget import TrigonometryWidget
from src.modules.functions.widget import FunctionsWidget
from src.modules.probability.widget import ProbabilityWidget
from src.modules.stereometry.widget import StereometryWidget
from src.modules.statistics.widget import StatisticsWidget
from src.modules.curriculum.widget import CurriculumWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MathTeach — Math Calculator & Tutor")
        self.stack = QStackedWidget()
        self.startup = StartupWidget(self.show_unit)
        self.algebra = AlgebraWidget(self.apply_geometry_equation)
        self.geometry = GeometryWidget()
        self.calculus = CalculusWidget()
        self.trigonometry = TrigonometryWidget()
        self.functions = FunctionsWidget()
        self.probability = ProbabilityWidget()
        self.stereometry = StereometryWidget()
        self.statistics = StatisticsWidget()
        self.curriculum = CurriculumWidget(self.show_topic)
        self.stack.addWidget(self.startup)
        self.stack.addWidget(self.algebra)
        self.stack.addWidget(self.geometry)
        self.stack.addWidget(self.calculus)
        self.stack.addWidget(self.trigonometry)
        self.stack.addWidget(self.functions)
        self.stack.addWidget(self.probability)
        self.stack.addWidget(self.stereometry)
        self.stack.addWidget(self.statistics)
        self.stack.addWidget(self.curriculum)
        self.setCentralWidget(self.stack)
        self.setMinimumSize(800, 600)
        self.stack.setCurrentWidget(self.startup)

    def show_unit(self, unit_name: str):
        if unit_name == 'algebra':
            self.stack.setCurrentWidget(self.algebra)
        elif unit_name == 'geometry':
            self.stack.setCurrentWidget(self.geometry)
        elif unit_name == 'calculus':
            self.stack.setCurrentWidget(self.calculus)
        elif unit_name == 'trigonometry':
            self.stack.setCurrentWidget(self.trigonometry)
        elif unit_name == 'functions':
            self.stack.setCurrentWidget(self.functions)
        elif unit_name == 'probability':
            self.stack.setCurrentWidget(self.probability)
        elif unit_name == 'stereometry':
            self.stack.setCurrentWidget(self.stereometry)
        elif unit_name == 'statistics':
            self.stack.setCurrentWidget(self.statistics)
        elif unit_name == 'curriculum':
            self.stack.setCurrentWidget(self.curriculum)
        else:
            # other units not implemented yet — return to startup
            self.stack.setCurrentWidget(self.startup)

    def show_topic(self, section, topic):
        # route to module based on topic name
        if 'equation' in topic.lower() or 'inequality' in topic.lower() or 'function' in section.lower():
            self.stack.setCurrentWidget(self.algebra)
        elif 'geometry' in section.lower() or 'triangle' in topic.lower() or 'circle' in topic.lower():
            self.stack.setCurrentWidget(self.geometry)
        elif 'stereometry' in section.lower():
            self.stack.setCurrentWidget(self.stereometry)
        elif 'trigonometry' in section.lower() or 'sin' in topic.lower() or 'cos' in topic.lower() or 'tan' in topic.lower():
            self.stack.setCurrentWidget(self.trigonometry)
        elif 'probability' in section.lower() or 'statistics' in section.lower() or 'combinatorics' in section.lower():
            self.stack.setCurrentWidget(self.probability)
        elif 'calculus' in section.lower() or 'limit' in topic.lower() or 'integral' in topic.lower():
            self.stack.setCurrentWidget(self.calculus)
        elif 'function' in section.lower() or 'quadratic' in topic.lower() or 'function' in topic.lower():
            self.stack.setCurrentWidget(self.functions)
        else:
            self.stack.setCurrentWidget(self.algebra)

    def apply_geometry_equation(self, equation: str) -> str:
        # Parse equation from Algebra and apply to geometry unit if available.
        if not hasattr(self, 'geometry') or self.geometry is None:
            return 'Geometry unit not available.'
        return self.geometry.apply_equation(equation)

