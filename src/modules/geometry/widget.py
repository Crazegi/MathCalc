from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTextEdit, QLineEdit, QComboBox, QCheckBox, QGraphicsScene, QGraphicsView, QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsTextItem
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPen, QBrush, QColor, QPainter, QFont
from PySide6.QtWidgets import QGraphicsItem
from dataclasses import dataclass
from typing import cast, Optional
import sympy as sp
import math
import json
import os
import random


@dataclass
class GeometryObjectMeta:
    kind: str
    name: str
    details: str


class PointItem(QGraphicsEllipseItem):
    def __init__(self, x, y, label, parent_widget):
        super().__init__(x - 5, y - 5, 10, 10)
        self.name = label
        self.parent_widget = parent_widget
        self.setBrush(QBrush(QColor('red')))
        self.setPen(QPen(QColor('black')))
        self.setZValue(1)
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
            | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
        )
        self.setData(0, label)

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange and self.parent_widget is not None:
            self.parent_widget.on_point_moved(self)
        return super().itemChange(change, value)


@dataclass
class LineObject:
    p1: PointItem
    p2: PointItem
    item: QGraphicsLineItem
    meta: GeometryObjectMeta


@dataclass
class CircleObject:
    center: PointItem
    boundary: PointItem
    item: QGraphicsEllipseItem
    meta: GeometryObjectMeta


class GeometryCanvas(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.mode = 'point'
        self.setSceneRect(-400, -300, 800, 600)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

    def mousePressEvent(self, event):
        scene_pt = self.mapToScene(event.pos())
        parent = cast('GeometryWidget', self.parent())
        if parent is None:
            return
        if self.mode == 'point':
            parent.add_point(scene_pt)
        else:
            parent.try_select_point(scene_pt)
        super().mousePressEvent(event)


class GeometryWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.points: list[PointItem] = []
        self.point_labels: list[QGraphicsTextItem] = []
        self.selected_points: list[PointItem] = []
        self.line_objects: list[LineObject] = []
        self.circle_objects: list[CircleObject] = []
        self.history: list[dict] = []

        self.canvas = GeometryCanvas(self)
        self.canvas.setMinimumSize(700, 500)
        self.canvas._scene.selectionChanged.connect(self.on_selection_changed)

        # Units selector
        self.unit_combo = QComboBox()
        self.unit_combo.addItems(['mm', 'cm', 'm'])
        self.unit_combo.currentTextChanged.connect(self.update_info_panel)
        self.unit_label = QLabel('Unit: mm')

        buttons_layout = QHBoxLayout()
        self.mode_label = QLabel('Mode: Add Point')
        self.status_label = QLabel('Click on the canvas to place a point')
        self.info_box = QTextEdit()
        self.info_box.setReadOnly(True)
        self.info_box.setFont(QFont('Courier', 10))
        self.info_box.setFixedHeight(180)

        add_point_btn = QPushButton('Add Point')
        add_line_btn = QPushButton('Add Line')
        add_circle_btn = QPushButton('Add Circle')
        add_angle_btn = QPushButton('Measure Angle')
        clear_btn = QPushButton('Clear All')

        add_point_btn.clicked.connect(lambda: self.set_mode('point'))
        add_line_btn.clicked.connect(lambda: self.set_mode('line'))
        add_circle_btn.clicked.connect(lambda: self.set_mode('circle'))
        add_angle_btn.clicked.connect(lambda: self.set_mode('angle'))
        clear_btn.clicked.connect(self.clear_all)

        self.triangle_analysis_btn = QPushButton('Triangle Analysis')
        self.triangle_analysis_btn.clicked.connect(self.triangle_analysis)
        self.vocab_checkbox = QCheckBox('Instructor vocabulary')
        self.vocab_checkbox.stateChanged.connect(self.update_info_panel)

        buttons_layout.addWidget(add_angle_btn)

        buttons_layout.addWidget(add_point_btn)
        buttons_layout.addWidget(add_line_btn)
        buttons_layout.addWidget(add_circle_btn)
        buttons_layout.addWidget(self.triangle_analysis_btn)
        buttons_layout.addWidget(clear_btn)
        buttons_layout.addWidget(self.vocab_checkbox)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.unit_label)
        buttons_layout.addWidget(self.unit_combo)

        equation_layout = QHBoxLayout()
        self.equation_input = QLineEdit()
        self.equation_input.setPlaceholderText('Enter line as y=mx+b or x=a or circle equation')
        self.equation_apply_button = QPushButton('Populate from line equation')
        self.equation_apply_button.clicked.connect(self.on_apply_equation_input)
        equation_layout.addWidget(self.equation_input)
        equation_layout.addWidget(self.equation_apply_button)

        undo_layout = QHBoxLayout()
        self.undo_button = QPushButton('Undo')
        self.undo_button.clicked.connect(self.undo_last)
        undo_layout.addWidget(self.undo_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(equation_layout)
        main_layout.addLayout(undo_layout)
        main_layout.addLayout(buttons_layout)
        main_layout.addWidget(self.mode_label)
        main_layout.addWidget(self.status_label)
        main_layout.addWidget(self.canvas)

        self.property_box = QTextEdit()
        self.property_box.setReadOnly(True)
        self.property_box.setFont(QFont('Courier', 10))
        self.property_box.setFixedHeight(120)
        main_layout.addWidget(QLabel('Selected object properties'))
        main_layout.addWidget(self.property_box)

        main_layout.addWidget(QLabel('Geometry Info'))
        main_layout.addWidget(self.info_box)

        practice_layout = QHBoxLayout()
        self.practice_load_btn = QPushButton('Load Practice Problem')
        self.practice_solve_btn = QPushButton('Solve Practice')
        self.practice_load_btn.clicked.connect(self.load_practice_problem)
        self.practice_solve_btn.clicked.connect(self.solve_practice_problem)
        practice_layout.addWidget(self.practice_load_btn)
        practice_layout.addWidget(self.practice_solve_btn)
        main_layout.addLayout(practice_layout)

        hint_layout = QHBoxLayout()
        self.hint1_btn = QPushButton('Hint 1')
        self.hint2_btn = QPushButton('Hint 2')
        self.hint_answer_btn = QPushButton('Show Answer')
        self.hint1_btn.clicked.connect(lambda: self.show_hint(1))
        self.hint2_btn.clicked.connect(lambda: self.show_hint(2))
        self.hint_answer_btn.clicked.connect(lambda: self.show_hint(3))
        hint_layout.addWidget(self.hint1_btn)
        hint_layout.addWidget(self.hint2_btn)
        hint_layout.addWidget(self.hint_answer_btn)
        main_layout.addLayout(hint_layout)

        # Suggestions and angle awareness
        self.suggestions_box = QTextEdit()
        self.suggestions_box.setReadOnly(True)
        self.suggestions_box.setFont(QFont('Courier', 10))
        self.suggestions_box.setFixedHeight(120)
        main_layout.addWidget(QLabel('Suggestions'))
        main_layout.addWidget(self.suggestions_box)

        self.setLayout(main_layout)

        self.set_mode('point')
        self.update_info_panel()

    def set_mode(self, mode):
        self.canvas.mode = mode
        self.selected_points = []
        self.mode_label.setText(f'Mode: {mode.capitalize()}')
        if mode == 'point':
            self.status_label.setText('Click to create points')
        elif mode == 'line':
            self.status_label.setText('Select two existing points to connect with a line')
        elif mode == 'circle':
            self.status_label.setText('Select center point then a point on circumference')
        elif mode == 'angle':
            self.status_label.setText('Select three points (vertex second) to measure angle')
        self.unit_label.setText(f'Unit: {self.unit_combo.currentText()}')


    def add_point(self, pos: QPointF):
        name = f'P{len(self.points)+1}'
        pt = PointItem(pos.x(), pos.y(), name, self)
        self.canvas._scene.addItem(pt)

        label = QGraphicsTextItem(name)
        label.setPos(pos.x() + 8, pos.y() + 8)
        label.setDefaultTextColor(QColor('black'))
        self.canvas._scene.addItem(label)

        self.points.append(pt)
        self.point_labels.append(label)
        self.status_label.setText(f'Created point {name} at ({pos.x():.1f}, {pos.y():.1f})')
        self.update_info_panel()

    def find_point(self, pos: QPointF):
        for pt in self.points:
            center = QPointF(pt.rect().x() + 5, pt.rect().y() + 5)
            dist = ((center.x() - pos.x())**2 + (center.y() - pos.y())**2)**0.5
            if dist <= 8:
                return pt
        return None

    def try_select_point(self, pos: QPointF):
        pt = self.find_point(pos)
        if pt is None:
            self.status_label.setText('No point near click; please select a point')
            return

        if pt in self.selected_points:
            self.status_label.setText(f'{pt.name} already selected')
            return

        self.selected_points.append(pt)
        self._highlight(pt)
        self.status_label.setText(f'Selected {pt.name} ({len(self.selected_points)}/2)')

        if self.canvas.mode == 'line' and len(self.selected_points) == 2:
            self._commit_line()
            self.selected_points = []
        elif self.canvas.mode == 'circle' and len(self.selected_points) == 2:
            self._commit_circle()
            self.selected_points = []
        elif self.canvas.mode == 'angle' and len(self.selected_points) == 3:
            self._commit_angle()
            self.selected_points = []

    def _highlight(self, pt: PointItem):
        pt.setBrush(QBrush(QColor('green')))

    def on_point_moved(self, pt: PointItem):
        idx = self.points.index(pt)
        label = self.point_labels[idx]
        label.setPos(pt.x() + 8, pt.y() + 8)
        self._refresh_geometry_objects()
        self.update_info_panel()

    def _commit_line(self):
        if len(self.selected_points) < 2:
            return
        p1, p2 = self.selected_points[0], self.selected_points[1]
        p1c = p1.rect().center() + p1.pos()
        p2c = p2.rect().center() + p2.pos()
        line_item = QGraphicsLineItem(p1c.x(), p1c.y(), p2c.x(), p2c.y())
        line_item.setPen(QPen(QColor('blue'), 2))
        line_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.canvas._scene.addItem(line_item)
        self.line_objects.append(LineObject(p1, p2, line_item, GeometryObjectMeta('line', f'{p1.name}{p2.name}', '')))
        self.history.append({'kind':'line_from_points','line':line_item,'p1':p1,'p2':p2})
        self.status_label.setText(f'Line {p1.name}{p2.name} created')
        self._clear_point_highlights()
        self.update_info_panel()

    def on_selection_changed(self):
        selected = self.canvas._scene.selectedItems()
        if not selected:
            self.property_box.clear()
            return
        item = selected[0]
        if isinstance(item, QGraphicsLineItem):
            for lo in self.line_objects:
                if lo.item is item:
                    self._populate_line_properties(lo)
                    break
        elif isinstance(item, QGraphicsEllipseItem):
            for co in self.circle_objects:
                if co.item is item:
                    self._populate_circle_properties(co)
                    break
        else:
            self.property_box.setPlainText(f'Selected: {item}')

    def _populate_line_properties(self, lo: LineObject):
        x1, y1 = lo.p1.rect().center().x() + lo.p1.pos().x(), lo.p1.rect().center().y() + lo.p1.pos().y()
        x2, y2 = lo.p2.rect().center().x() + lo.p2.pos().x(), lo.p2.rect().center().y() + lo.p2.pos().y()
        dx, dy = x2 - x1, y2 - y1
        slope = dy / dx if abs(dx) > 1e-6 else float('inf')
        intercept = y1 - slope * x1 if slope != float('inf') else None
        props = [f'Line: {lo.p1.name}{lo.p2.name}', f'Slope: {slope:.4f}' if slope != float('inf') else 'Slope: vertical', f'Intercept: {intercept:.4f}' if intercept is not None else 'Intercept: N/A']
        self.property_box.setPlainText('\n'.join(props))

    def _populate_circle_properties(self, co: CircleObject):
        cx, cy = co.center.rect().center().x() + co.center.pos().x(), co.center.rect().center().y() + co.center.pos().y()
        bx, by = co.boundary.rect().center().x() + co.boundary.pos().x(), co.boundary.rect().center().y() + co.boundary.pos().y()
        r = math.hypot(cx - bx, cy - by)
        props = [f'Circle center: ({cx:.2f}, {cy:.2f})', f'Radius: {r:.2f}', f'Equation: (x - {cx:.2f})^2 + (y - {cy:.2f})^2 = {r:.2f}^2']
        self.property_box.setPlainText('\n'.join(props))

    def triangle_analysis(self):
        if len(self.points) < 3:
            self.status_label.setText('Need 3 points for triangle analysis')
            return
        a,b,c = self.points[0], self.points[1], self.points[2]
        _, steps = self._triangle_area_details(a,b,c)
        alt_a = self._triangle_altitude(a,b,c)
        alt_b = self._triangle_altitude(b,c,a)
        alt_c = self._triangle_altitude(c,a,b)
        self.suggestions_box.setPlainText('\n'.join(steps + [f'Altitudes: from A {alt_a:.2f}, from B {alt_b:.2f}, from C {alt_c:.2f}']))

    def _triangle_altitude(self, vertex: PointItem, p1: PointItem, p2: PointItem) -> float:
        vx, vy = vertex.pos().x(), vertex.pos().y()
        x1,y1 = p1.pos().x(), p1.pos().y()
        x2,y2 = p2.pos().x(), p2.pos().y()
        area_2 = abs((x1-vx)*(y2-vy) - (x2-vx)*(y1-vy))
        base = math.hypot(x2-x1, y2-y1)
        return (2*area_2/base) if base!=0 else 0

    def load_practice_problem(self):
        problems_path = os.path.join(os.getcwd(), 'data', 'practice_problems.json')
        os.makedirs(os.path.dirname(problems_path), exist_ok=True)
        if not os.path.exists(problems_path):
            default = [
                {
                    'id': 1,
                    'question': 'Given triangle with A(0,0), B(4,0), C(0,3), compute area.',
                    'answer': 6.0,
                    'type': 'triangle_area',
                    'points': [[0,0],[4,0],[0,3]]
                }
            ]
            with open(problems_path, 'w', encoding='utf-8') as f:
                json.dump(default, f, indent=2)

        with open(problems_path, 'r', encoding='utf-8') as f:
            problems = json.load(f)
        self.current_problem = random.choice(problems)
        self.status_label.setText(f"Loaded problem {self.current_problem['id']}: {self.current_problem['question']}")
        self.suggestions_box.setPlainText('')

    def solve_practice_problem(self):
        if not hasattr(self, 'current_problem') or self.current_problem is None:
            self.status_label.setText('No practice problem loaded.')
            return
        prob = self.current_problem
        result = None
        if prob.get('type') == 'triangle_area':
            pts = prob.get('points')
            a,b,c = pts
            area = abs(0.5 * ((a[0]*(b[1]-c[1]) + b[0]*(c[1]-a[1]) + c[0]*(a[1]-b[1]))))
            result = area
        log_line = f"problem={prob['id']} computed={result} expected={prob['answer']}"
        os.makedirs('logs', exist_ok=True)
        with open('logs/practice.log', 'a', encoding='utf-8') as logf:
            logf.write(log_line + '\n')
        self.status_label.setText(f"Solved: {result}, expected: {prob['answer']}")
        self.suggestions_box.setPlainText(log_line)

    def show_hint(self, level:int):
        if len(self.points) < 3:
            self.status_label.setText('Add at least 3 points based on instructions')
            return
        a,b,c = self.points[0], self.points[1], self.points[2]
        if level==1:
            self.suggestions_box.setPlainText(f'Hint 1: Compute AB distance. AB = {self._formatted_length(self._point_distance(a,b))}')
        elif level==2:
            angB = self._angle_degrees(a.pos(), b.pos(), c.pos())
            self.suggestions_box.setPlainText(f'Hint 2: Compute angle at B: {angB:.2f}\u00b0')
        else:
            area,_ = self._triangle_area_details(a,b,c)
            self.suggestions_box.setPlainText(f'Answer: Triangle area = {area:.2f} {self.unit_combo.currentText()}^2')

    def _commit_circle(self):
        c, b = self.selected_points
        cpos = c.rect().center() + c.pos()
        bpos = b.rect().center() + b.pos()
        r = ((cpos.x()-bpos.x())**2 + (cpos.y()-bpos.y())**2)**0.5
        circle_item = QGraphicsEllipseItem(cpos.x() - r, cpos.y() - r, 2*r, 2*r)
        circle_item.setPen(QPen(QColor('magenta'), 2))
        self.canvas._scene.addItem(circle_item)

        circle_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.circle_objects.append(CircleObject(c, b, circle_item, GeometryObjectMeta('circle', f'{c.name}R', '')))
        self.history.append({'kind':'circle_from_points','circle':circle_item,'center':c,'boundary':b})
        self.status_label.setText(f'Circle centered at {c.name} radius {self._formatted_length(r)}')
        self._clear_point_highlights()
        self.update_info_panel()

    def _commit_angle(self):
        a, b, c = self.selected_points
        angle_deg = self._angle_degrees(a.pos(), b.pos(), c.pos())
        self.status_label.setText(f'Angle {a.name}{b.name}{c.name}: {angle_deg:.1f}\u00b0')
        # Suggest using the angle for triangle and geometry reasoning.
        self.update_info_panel()

    def _refresh_geometry_objects(self):
        for line in self.line_objects:
            p1c = line.p1.rect().center() + line.p1.pos()
            p2c = line.p2.rect().center() + line.p2.pos()
            line.item.setLine(p1c.x(), p1c.y(), p2c.x(), p2c.y())

        for circ in self.circle_objects:
            cpos = circ.center.rect().center() + circ.center.pos()
            bpos = circ.boundary.rect().center() + circ.boundary.pos()
            r = ((cpos.x()-bpos.x())**2 + (cpos.y()-bpos.y())**2)**0.5
            circ.item.setRect(cpos.x() - r, cpos.y() - r, 2*r, 2*r)

    def _add_point_item(self, x: float, y: float, name: str) -> PointItem:
        pt = PointItem(x, y, name, self)
        self.canvas._scene.addItem(pt)
        label = QGraphicsTextItem(name)
        label.setPos(x + 8, y + 8)
        label.setDefaultTextColor(QColor('black'))
        self.canvas._scene.addItem(label)
        self.points.append(pt)
        self.point_labels.append(label)
        return pt

    def add_line_from_equation(self, m: float, b: float):
        p1 = self._add_point_item(-100, -100 * m + b, f'L{len(self.points)+1}')
        p2 = self._add_point_item(100, 100 * m + b, f'L{len(self.points)+1}')
        line_item = QGraphicsLineItem(p1.rect().center().x() + p1.pos().x(), p1.rect().center().y() + p1.pos().y(), p2.rect().center().x() + p2.pos().x(), p2.rect().center().y() + p2.pos().y())
        line_item.setPen(QPen(QColor('blue'), 2))
        line_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.canvas._scene.addItem(line_item)
        self.line_objects.append(LineObject(p1, p2, line_item, GeometryObjectMeta('line', f'{p1.name}{p2.name}', '')))
        self.history.append({'kind':'line_from_eq','line':line_item,'p1':p1,'p2':p2})
        self.status_label.setText(f'Equation line added: y = {m:.3f}x + {b:.3f}')
        self.update_info_panel()

    def add_vertical_line(self, x_val: float):
        y1, y2 = -100, 100
        p1 = self._add_point_item(x_val, y1, f'V{len(self.points)+1}')
        p2 = self._add_point_item(x_val, y2, f'V{len(self.points)+1}')
        line_item = QGraphicsLineItem(x_val, y1, x_val, y2)
        line_item.setPen(QPen(QColor('blue'), 2))
        self.canvas._scene.addItem(line_item)
        self.line_objects.append(LineObject(p1, p2, line_item, GeometryObjectMeta('line', f'{p1.name}{p2.name}', 'vertical line')))
        self.status_label.setText(f'Equation line added: x = {x_val:.2f}')
        self.history.append({'kind':'line_from_eq','line':line_item,'p1':p1,'p2':p2})
        self.update_info_panel()

    def add_circle_from_equation(self, cx: float, cy: float, r: float):
        center = self._add_point_item(cx, cy, f'C{len(self.points)+1}')
        boundary = self._add_point_item(cx + r, cy, f'C{len(self.points)+1}')
        circle_item = QGraphicsEllipseItem(cx - r, cy - r, 2*r, 2*r)
        circle_item.setPen(QPen(QColor('magenta'), 2))
        self.canvas._scene.addItem(circle_item)
        self.circle_objects.append(CircleObject(center, boundary, circle_item, GeometryObjectMeta('circle', f'{center.name}_{boundary.name}', 'equation circle')))
        self.history.append({'kind':'circle_from_eq','circle':circle_item,'center':center,'boundary':boundary})
        self.status_label.setText(f'Equation circle added: center ({cx:.2f}, {cy:.2f}) r={r:.2f}')
        self.update_info_panel()

    def apply_equation(self, command: str) -> str:
        try:
            parts = command.split(':')
            kind = parts[0]
            if kind == 'line' and len(parts) == 3:
                m, b = float(parts[1]), float(parts[2])
                self.add_line_from_equation(m, b)
                return f'Applied line y = {m:.3f}x + {b:.3f}'
            if kind == 'vertical' and len(parts) == 2:
                x = float(parts[1])
                self.add_vertical_line(x)
                return f'Applied line x = {x:.2f}'
            if kind == 'circle' and len(parts) == 4:
                cx, cy, r = float(parts[1]), float(parts[2]), float(parts[3])
                self.add_circle_from_equation(cx, cy, r)
                return f'Applied circle center=({cx:.2f},{cy:.2f}), r={r:.2f}'
            return 'Unsupported geometry command.'
        except Exception as e:
            return f'Geometry apply error: {e}'

    def _unit_scale(self):
        unit = self.unit_combo.currentText()
        return {
            'mm': 1.0,
            'cm': 0.1,
            'm': 0.001
        }.get(unit, 1.0)

    def _formatted_length(self, length_px: float) -> str:
        scale = self._unit_scale()
        unit = self.unit_combo.currentText()
        return f"{length_px*scale:.2f} {unit}"

    def _angle_degrees(self, p1, vertex, p2):
        v1 = (p1.x() - vertex.x(), p1.y() - vertex.y())
        v2 = (p2.x() - vertex.x(), p2.y() - vertex.y())
        dot = v1[0]*v2[0] + v1[1]*v2[1]
        mag1 = math.hypot(*v1)
        mag2 = math.hypot(*v2)
        if mag1 == 0 or mag2 == 0:
            return 0.0
        cosang = max(-1.0, min(1.0, dot / (mag1*mag2)))
        return math.degrees(math.acos(cosang))

    def _triangle_area_details(self, a: PointItem, b: PointItem, c: PointItem):
        ax, ay = a.rect().center().x() + a.pos().x(), a.rect().center().y() + a.pos().y()
        bx, by = b.rect().center().x() + b.pos().x(), b.rect().center().y() + b.pos().y()
        cx, cy = c.rect().center().x() + c.pos().x(), c.rect().center().y() + c.pos().y()
        area = abs(0.5 * ((ax*(by-cy) + bx*(cy-ay) + cx*(ay-by))))
        factor = self._unit_scale()
        unit = self.unit_combo.currentText()
        area_unit = f"{unit}^2"
        scaled_area = area * factor * factor
        steps = [
            f"Triangle {a.name}{b.name}{c.name} coordinates: A({ax:.2f},{ay:.2f}), B({bx:.2f},{by:.2f}), C({cx:.2f},{cy:.2f})",
            "Use determinant formula: area = 0.5 * | x1(y2-y3) + x2(y3-y1) + x3(y1-y2) |",
            f"Calculated raw area: {area:.2f} px^2 = {scaled_area:.2f} {area_unit}",
        ]
        return scaled_area, steps

    def _compute_suggestions(self):
        suggestions = []
        if len(self.points) >= 2:
            p = self.points[-2]
            q = self.points[-1]
            dist = self._point_distance(p, q)
            suggestions.append(f"Distance {p.name}{q.name}: {self._formatted_length(dist)}")
        
        self.suggestions_box.setPlainText('')

        if len(self.points) >= 3:
            triplets = [self.points[i:i+3] for i in range(len(self.points)-2)]
            for i, (a,b,c) in enumerate(triplets,1):
                ang = self._angle_degrees(a.pos(), b.pos(), c.pos())
                suggestions.append(f"Angle {a.name}{b.name}{c.name}: {ang:.1f}\u00b0")
            # auto-calc area for first triangle
            a0,b0,c0 = triplets[0]
            tri_area, derivation = self._triangle_area_details(a0,b0,c0)
            suggestions.append(f"Triangle {a0.name}{b0.name}{c0.name} area: {tri_area:.2f} {self.unit_combo.currentText()}^2")
            suggestions.extend(derivation)

        if self.line_objects:
            suggestions.append('Suggest: compute slope and intercept for created lines')
        if self.circle_objects:
            suggestions.append('Suggest: compute area and circumference for created circles')

        # Theorem suggestions
        if len(self.points) >= 3:
            steps = self.build_theorem_steps()
            suggestions.extend(steps)

        if len(self.line_objects) >= 2:
            suggestions.append('Theorem: check if two lines are parallel or perpendicular by slope.')
            if self.vocab_checkbox.isChecked():
                suggestions.append('Vocabulary: Parallel Lines, Perpendicular Lines, Slope')

        if self.vocab_checkbox.isChecked() and len(self.points) >= 3:
            suggestions.append('Vocabulary: Law of Cosines, Law of Sines, Pythagorean Theorem')

        self.suggestions_box.setPlainText('\n'.join(suggestions))

    def on_apply_equation_input(self):
        equation_text = self.equation_input.text().strip()
        if not equation_text:
            self.status_label.setText('Enter equation first')
            return
        try:
            cmd = self._parse_equation_command(equation_text)
            result = self.apply_equation(cmd)
            self.status_label.setText(result)
            self.update_info_panel()
        except Exception as e:
            self.status_label.setText(f'Parse error: {e}')

    def _parse_equation_command(self, equation_text: str) -> str:
        eq_text = equation_text.strip().replace('^', '**')
        x, y = sp.symbols('x y')
        if eq_text.startswith('y='):
            right = eq_text[2:]
            expr = sp.sympify(right)
            m = sp.simplify(sp.diff(expr, x))
            b = expr.subs(x, 0)
            return f'line:{float(m)}:{float(b)}'
        if eq_text.startswith('x='):
            xval = float(eq_text[2:])
            return f'vertical:{xval}'
        if '=' in eq_text:
            lhs, rhs = eq_text.split('=', 1)
            lhs_expr = sp.sympify(lhs)
            rhs_expr = sp.sympify(rhs)
            expr = sp.simplify(lhs_expr - rhs_expr)  # type: ignore
            if expr.has(x**2) and expr.has(y**2):
                # attempt circle detection
                cx = -expr.coeff(x, 1)/2
                cy = -expr.coeff(y, 1)/2
                c = expr.subs({x:0, y:0})
                r = sp.sqrt(cx**2 + cy**2 - c)
                return f'circle:{float(cx)}:{float(cy)}:{float(r)}'
        raise ValueError('Unsupported equation format')

    def _remove_point_item(self, pt: PointItem):
        if pt not in self.points:
            return
        idx = self.points.index(pt)
        label = self.point_labels[idx]
        self.canvas._scene.removeItem(label)
        self.canvas._scene.removeItem(pt)
        self.points.pop(idx)
        self.point_labels.pop(idx)

    def undo_last(self):
        if not self.history:
            self.status_label.setText('Nothing to undo.')
            return
        action = self.history.pop()
        kind = action.get('kind')
        if kind in ['line_from_eq', 'line_from_points']:
            self.canvas._scene.removeItem(action['line'])
            self.line_objects = [l for l in self.line_objects if l.item is not action['line']]
            # do not remove points for line_from_points as user points could be shared
            if kind == 'line_from_eq':
                self._remove_point_item(action['p1'])
                self._remove_point_item(action['p2'])
            self.status_label.setText('Undid line creation')
        elif kind in ['circle_from_eq', 'circle_from_points']:
            self.canvas._scene.removeItem(action['circle'])
            self.circle_objects = [c for c in self.circle_objects if c.item is not action['circle']]
            if kind == 'circle_from_eq':
                self._remove_point_item(action['center'])
                self._remove_point_item(action['boundary'])
            self.status_label.setText('Undid circle creation')
        else:
            self.status_label.setText('Unknown undo action')
        self.update_info_panel()

    def build_theorem_steps(self):
        if len(self.points) < 3:
            return ["Add at least 3 points to start triangle theorem steps."]
        a, b, c = self.points[0], self.points[1], self.points[2]
        steps = []
        steps.append(f"Given triangle {a.name}{b.name}{c.name}:")
        steps.append(f"1. Calculate side lengths {a.name}{b.name}, {b.name}{c.name}, {c.name}{a.name}.")
        steps.append(f"2. Compute angles at {a.name}, {b.name}, {c.name} using law of cosines.")
        steps.append(f"3. Check whether psi theorem holds (sum of angles = 180°).")
        steps.append(f"4. If any angle is 90°, the triangle is right-angled (Pythagorean theorem).")
        return steps

    def _clear_point_highlights(self):
        for pt in self.points:
            pt.setBrush(QBrush(QColor('red')))

    def _point_distance(self, p1: PointItem, p2: PointItem) -> float:
        p1c = p1.rect().center() + p1.pos()
        p2c = p2.rect().center() + p2.pos()
        return math.hypot(p2c.x() - p1c.x(), p2c.y() - p1c.y())

    def geometry_line_equation(self, lo: LineObject) -> str:
        x1, y1 = lo.p1.rect().center().x() + lo.p1.pos().x(), lo.p1.rect().center().y() + lo.p1.pos().y()
        x2, y2 = lo.p2.rect().center().x() + lo.p2.pos().x(), lo.p2.rect().center().y() + lo.p2.pos().y()
        if abs(x1 - x2) < 1e-6:
            return f'x = {x1:.2f}'
        m = (y2 - y1) / (x2 - x1)
        b = y1 - m * x1
        return f'y = {m:.3f}x + {b:.3f}'

    def geometry_circle_equation(self, co: CircleObject) -> str:
        cx, cy = co.center.rect().center().x() + co.center.pos().x(), co.center.rect().center().y() + co.center.pos().y()
        bx, by = co.boundary.rect().center().x() + co.boundary.pos().x(), co.boundary.rect().center().y() + co.boundary.pos().y()
        r = ((cx-bx)**2 + (cy-by)**2)**0.5
        return f'(x - {cx:.2f})^2 + (y - {cy:.2f})^2 = {r:.2f}^2'

    def update_info_panel(self):
        lines = ['Points:']
        factor = self._unit_scale()
        unit = self.unit_combo.currentText()
        for pt in self.points:
            x, y = pt.rect().center().x() + pt.pos().x(), pt.rect().center().y() + pt.pos().y()
            lines.append(f'  {pt.name}: ({x*factor:.2f}, {y*factor:.2f}) {unit}')

        if self.line_objects:
            lines.append('Lines:')
            for i, lo in enumerate(self.line_objects, 1):
                eq = self.geometry_line_equation(lo)
                p = lo.p1
                q = lo.p2
                dist_px = ((p.rect().center().x()+p.pos().x()-q.rect().center().x()-q.pos().x())**2 + (p.rect().center().y()+p.pos().y()-q.rect().center().y()-q.pos().y())**2)**0.5
                lines.append(f'  L{i} {p.name}{q.name}: {eq} (length {self._formatted_length(dist_px)})')

        if self.circle_objects:
            lines.append('Circles:')
            for i, co in enumerate(self.circle_objects, 1):
                eq = self.geometry_circle_equation(co)
                cpos = co.center.rect().center() + co.center.pos()
                bpos = co.boundary.rect().center() + co.boundary.pos()
                radius_px = math.hypot(cpos.x()-bpos.x(), cpos.y()-bpos.y())
                lines.append(f'  C{i} center={co.center.name}, rpt={co.boundary.name}: {eq} (r={self._formatted_length(radius_px)})')

        self.info_box.setPlainText('\n'.join(lines))
        self._compute_suggestions()

    def clear_all(self):
        self.canvas._scene.clear()
        self.points.clear()
        self.point_labels.clear()
        self.selected_points.clear()
        self.line_objects.clear()
        self.circle_objects.clear()
        self.status_label.setText('Canvas cleared.')
        self.update_info_panel()
