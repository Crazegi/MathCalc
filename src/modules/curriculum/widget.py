from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton,
    QScrollArea, QLineEdit, QHBoxLayout, QGroupBox, QCheckBox, QTextEdit)
from PySide6.QtCore import Qt
from src.engine.math_engine import MathEngine
import xml.etree.ElementTree as ET
import os
import json

class CurriculumWidget(QWidget):
    def __init__(self, on_select_topic=None):
        super().__init__()
        self.on_select_topic = on_select_topic
        self.checkboxes = {}
        self.curriculum = self.load_curriculum()
        self.engine = MathEngine()

        self.progress_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'curriculum_progress.json')
        self.progress_state = self.load_progress()

        self.main_layout = QVBoxLayout()
        header = QLabel("Curriculum Guide")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("font-size: 18pt; font-weight: bold;")
        self.main_layout.addWidget(header)

        subtitle = QLabel("Phase A & B: full base level path (Reals, Eqns, Funcs, Seqs, Trig, Geometry, Stereometry, Stats)")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(subtitle)

        self.progress_label = QLabel("Progress: 0 of 0 topics complete")
        self.main_layout.addWidget(self.progress_label)

        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search topics...")
        self.search_input.textChanged.connect(self.render_topics)
        self.reset_button = QPushButton("Reset Progress")
        self.reset_button.clicked.connect(self.reset_progress)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.reset_button)
        self.main_layout.addLayout(search_layout)

        self.content_area = QScrollArea()
        self.content_area.setWidgetResizable(True)
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_widget.setLayout(self.content_layout)
        self.content_area.setWidget(self.content_widget)

        self.main_layout.addWidget(self.content_area)

        self.topic_info = QTextEdit()
        self.topic_info.setReadOnly(True)
        self.topic_info.setFixedHeight(120)
        self.main_layout.addWidget(self.topic_info)

        self.exercise_label = QLabel("Practice question will appear here after selecting topic")
        self.exercise_label.setWordWrap(True)
        self.main_layout.addWidget(self.exercise_label)

        exercise_input_layout = QHBoxLayout()
        self.exercise_answer_input = QLineEdit()
        self.exercise_answer_input.setPlaceholderText("Enter your answer")
        self.check_answer_button = QPushButton("Check Answer")
        self.check_answer_button.clicked.connect(self.check_answer)
        self.generate_button = QPushButton("Generate Practice")
        self.generate_button.clicked.connect(self.generate_problem)
        exercise_input_layout.addWidget(self.exercise_answer_input)
        exercise_input_layout.addWidget(self.check_answer_button)
        exercise_input_layout.addWidget(self.generate_button)
        self.main_layout.addLayout(exercise_input_layout)

        self.setLayout(self.main_layout)

        self.current_question = None
        self.current_answer = None

        self.render_topics()

    def load_curriculum(self):
        # Try to load list.xml from repository root
        current_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        xml_path = os.path.normpath(os.path.join(current_dir, '..', '..', 'list.xml'))
        if not os.path.exists(xml_path):
            xml_path = os.path.normpath(os.path.join(current_dir, '..', 'list.xml'))

        if not os.path.exists(xml_path):
            return []

        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            sections = []
            for sec in root.findall('.//section'):
                title = sec.get('title', 'Unnamed Section')
                topics = [t.text.strip() for t in sec.findall('topic') if t.text]
                sections.append((title, topics))
            return sections
        except Exception as e:
            print(f"Curriculum load error: {e}")
            return []

    def render_topics(self):
        for i in reversed(range(self.content_layout.count())):
            item = self.content_layout.takeAt(i)
            if item is None:
                continue
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        query = self.search_input.text().lower().strip()
        total = 0
        completed = 0
        for section, topics in self.curriculum:
            if query and query not in section.lower() and not any(query in t.lower() for t in topics):
                continue
            group_box = QGroupBox(section)
            group_layout = QVBoxLayout()
            group_box.setLayout(group_layout)

            for topic in topics:
                if query and query not in topic.lower():
                    continue
                total += 1
                if topic not in self.checkboxes:
                    self.checkboxes[topic] = QCheckBox(topic)
                checkbox = self.checkboxes[topic]
                checkbox.setChecked(self.progress_state.get(topic, False))
                if checkbox not in self.content_widget.findChildren(QCheckBox):
                    checkbox.stateChanged.connect(self.update_progress)
                if checkbox.isChecked():
                    completed += 1

                button = QPushButton("Start")
                button.setMinimumWidth(90)
                button.clicked.connect(lambda checked, s=section, t=topic: self.start_topic(s, t))

                item_layout = QHBoxLayout()
                item_layout.addWidget(checkbox)
                item_layout.addWidget(button)
                group_layout.addLayout(item_layout)
            self.content_layout.addWidget(group_box)

        self.progress_label.setText(f"Progress: {completed} of {total} topics complete")

    def load_progress(self):
        if not os.path.exists(self.progress_file):
            return {}
        try:
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}

    def save_progress(self):
        try:
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(self.progress_state, f, indent=2)
        except Exception:
            pass

    def update_progress(self):
        completed = sum(1 for cb in self.checkboxes.values() if cb.isChecked())
        total = len(self.checkboxes)
        self.progress_label.setText(f"Progress: {completed} of {total} topics complete")
        for topic, checkbox in self.checkboxes.items():
            self.progress_state[topic] = checkbox.isChecked()
        self.save_progress()

    def reset_progress(self):
        for checkbox in self.checkboxes.values():
            checkbox.setChecked(False)
        self.update_progress()
        self.topic_info.clear()

    def start_topic(self, section, topic):
        details = self.get_topic_details(section, topic)
        self.topic_info.setPlainText(details)
        self.current_section = section
        self.current_topic = topic
        self.generate_problem()
        if self.on_select_topic:
            self.on_select_topic(section, topic)

    def generate_problem(self):
        if not hasattr(self, 'current_section') or not hasattr(self, 'current_topic'):
            self.exercise_label.setText("Select a topic first.")
            return
        q, a, hints = self.engine.generate_practice(self.current_section, self.current_topic)
        self.current_question = q
        self.current_answer = a
        hint_text = '\n'.join(hints)
        self.exercise_label.setText(f"Question: {q}\nHints: {hint_text}")
        self.exercise_answer_input.clear()

    def check_answer(self):
        if self.current_question is None:
            self.exercise_label.setText("Generate a practice question first.")
            return
        user_ans = self.exercise_answer_input.text().strip()
        if self.engine.check_practice(self.current_answer, user_ans):
            self.exercise_label.setText(f"Correct! {self.current_question} answer is {self.current_answer}")
        else:
            self.exercise_label.setText(f"Incorrect. Try again. {self.current_question} expected: {self.current_answer}")

    def get_topic_details(self, section, topic):
        description = f"Section: {section}\nTopic: {topic}\n\n"
        if 'real' in section.lower() or 'absolute value' in topic.lower() or 'percentages' in topic.lower():
            description += "Practice with expression simplification, inequality solving, and transformation using Algebra unit."
        elif 'equation' in section.lower() or 'inequality' in section.lower():
            description += "Use Algebra solver for linear and quadratic equations and inequalities; visualize with graph plots."
        elif 'function' in section.lower() or 'sequence' in section.lower():
            description += "Analyze domain, range, monotonicity; for sequences use iterative formulas and sums."
        elif 'trigonometry' in section.lower():
            description += "Use Trigonometry module for sin/cos/tan evaluation and identity manipulation."
        elif 'geometry' in section.lower() or 'stereometry' in section.lower():
            description += "Use Geometry module for plane and spatial reasoning; construct triangles, circles, and polygons."
        elif 'statistics' in section.lower() or 'probability' in section.lower() or 'combinatorics' in section.lower():
            description += "Use Algebra module for statistics/probability calculations, including mean/median/mode/stddev and basic combinatorics."
        else:
            description += "Use appropriate module to solve and visualize this topic."
        return description
