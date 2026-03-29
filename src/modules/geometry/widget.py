from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTextEdit, QGraphicsScene, QGraphicsView, QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsTextItem
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPen, QBrush, QColor, QPainter, QFont
from PySide6.QtWidgets import QGraphicsItem
from dataclasses import dataclass
from typing import cast
import sympy as sp


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


@dataclass
class CircleObject:
    center: PointItem
    boundary: PointItem
    item: QGraphicsEllipseItem


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

        self.canvas = GeometryCanvas(self)
        self.canvas.setMinimumSize(700, 500)

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
        clear_btn = QPushButton('Clear All')

        add_point_btn.clicked.connect(lambda: self.set_mode('point'))
        add_line_btn.clicked.connect(lambda: self.set_mode('line'))
        add_circle_btn.clicked.connect(lambda: self.set_mode('circle'))
        clear_btn.clicked.connect(self.clear_all)

        buttons_layout.addWidget(add_point_btn)
        buttons_layout.addWidget(add_line_btn)
        buttons_layout.addWidget(add_circle_btn)
        buttons_layout.addWidget(clear_btn)

        main_layout = QVBoxLayout()
        main_layout.addLayout(buttons_layout)
        main_layout.addWidget(self.mode_label)
        main_layout.addWidget(self.status_label)
        main_layout.addWidget(self.canvas)
        main_layout.addWidget(QLabel('Geometry Info'))
        main_layout.addWidget(self.info_box)
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

    def _highlight(self, pt: PointItem):
        pt.setBrush(QBrush(QColor('green')))

    def on_point_moved(self, pt: PointItem):
        idx = self.points.index(pt)
        label = self.point_labels[idx]
        label.setPos(pt.x() + 8, pt.y() + 8)
        self._refresh_geometry_objects()
        self.update_info_panel()

    def _commit_line(self):
        p1, p2 = self.selected_points
        p1c = p1.rect().center() + p1.pos()
        p2c = p2.rect().center() + p2.pos()
        line_item = QGraphicsLineItem(p1c.x(), p1c.y(), p2c.x(), p2c.y())
        line_item.setPen(QPen(QColor('blue'), 2))
        self.canvas._scene.addItem(line_item)

        self.line_objects.append(LineObject(p1, p2, line_item))
        self.status_label.setText(f'Line {p1.name}{p2.name} created')
        self._clear_point_highlights()
        self.update_info_panel()

    def _commit_circle(self):
        c, b = self.selected_points
        cpos = c.rect().center() + c.pos()
        bpos = b.rect().center() + b.pos()
        r = ((cpos.x()-bpos.x())**2 + (cpos.y()-bpos.y())**2)**0.5
        circle_item = QGraphicsEllipseItem(cpos.x() - r, cpos.y() - r, 2*r, 2*r)
        circle_item.setPen(QPen(QColor('magenta'), 2))
        self.canvas._scene.addItem(circle_item)

        self.circle_objects.append(CircleObject(c, b, circle_item))
        self.status_label.setText(f'Circle centered at {c.name} radius {r:.1f}')
        self._clear_point_highlights()
        self.update_info_panel()

    def _clear_point_highlights(self):
        for pt in self.points:
            pt.setBrush(QBrush(QColor('red')))

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
        for pt in self.points:
            x, y = pt.rect().center().x() + pt.pos().x(), pt.rect().center().y() + pt.pos().y()
            lines.append(f'  {pt.name}: ({x:.2f}, {y:.2f})')

        if self.line_objects:
            lines.append('Lines:')
            for i, lo in enumerate(self.line_objects, 1):
                eq = self.geometry_line_equation(lo)
                p = lo.p1
                q = lo.p2
                dist = ((p.rect().center().x()+p.pos().x()-q.rect().center().x()-q.pos().x())**2 + (p.rect().center().y()+p.pos().y()-q.rect().center().y()-q.pos().y())**2)**0.5
                lines.append(f'  L{i} {p.name}{q.name}: {eq} (length {dist:.2f})')

        if self.circle_objects:
            lines.append('Circles:')
            for i, co in enumerate(self.circle_objects, 1):
                eq = self.geometry_circle_equation(co)
                lines.append(f'  C{i} center={co.center.name}, rpt={co.boundary.name}: {eq}')

        self.info_box.setPlainText('\n'.join(lines))

    def clear_all(self):
        self.canvas._scene.clear()
        self.points.clear()
        self.point_labels.clear()
        self.selected_points.clear()
        self.line_objects.clear()
        self.circle_objects.clear()
        self.status_label.setText('Canvas cleared.')
        self.update_info_panel()
