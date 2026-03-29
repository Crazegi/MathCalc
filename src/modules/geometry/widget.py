from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QGraphicsScene, QGraphicsView, QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsTextItem
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPen, QBrush, QColor, QPainter
from typing import cast


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
        if self.mode == 'point':
            parent.add_point(scene_pt)
        else:
            parent.try_select_point(scene_pt)
        super().mousePressEvent(event)


class GeometryWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.points = []
        self.point_labels = []
        self.selected_points = []
        self.lines = []
        self.circles = []

        self.canvas = GeometryCanvas(self)
        self.canvas.setMinimumSize(700, 500)

        buttons_layout = QHBoxLayout()
        self.mode_label = QLabel("Mode: Add point")
        self.status_label = QLabel("Click on the canvas to place a point")

        add_point_btn = QPushButton("Add Point")
        add_line_btn = QPushButton("Add Line")
        add_circle_btn = QPushButton("Add Circle")
        clear_btn = QPushButton("Clear All")

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
        self.setLayout(main_layout)

        self.set_mode('point')

    def set_mode(self, mode):
        self.canvas.mode = mode
        self.selected_points = []
        self.mode_label.setText(f"Mode: {mode.capitalize()}")
        if mode == 'point':
            self.status_label.setText('Click to create points')
        elif mode == 'line':
            self.status_label.setText('Select two existing points to connect with a line')
        elif mode == 'circle':
            self.status_label.setText('Select center point then a point on circumference')

    def add_point(self, pos: QPointF):
        index = len(self.points) + 1
        item = QGraphicsEllipseItem(pos.x() - 5, pos.y() - 5, 10, 10)
        item.setBrush(QBrush(QColor('red')))
        item.setPen(QPen(QColor('black')))
        item.setZValue(1)
        item.setData(0, f"P{index}")
        self.canvas._scene.addItem(item)
        label = QGraphicsTextItem(f"P{index}")
        label.setPos(pos.x() + 8, pos.y() + 8)
        label.setDefaultTextColor(QColor('black'))
        self.canvas._scene.addItem(label)
        self.points.append(item)
        self.point_labels.append(label)
        self.status_label.setText(f"Created point P{index} at ({pos.x():.1f}, {pos.y():.1f})")

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
            self.status_label.setText('No point near click. Please select a point in shape mode.')
            return

        tag = pt.data(0)
        if pt in self.selected_points:
            return

        self.selected_points.append(pt)
        self._highlight(pt)
        self.status_label.setText(f"Selected {tag} ({len(self.selected_points)}/2)")

        if self.canvas.mode == 'line' and len(self.selected_points) == 2:
            self._commit_line()
            self.selected_points = []
        elif self.canvas.mode == 'circle' and len(self.selected_points) == 2:
            self._commit_circle()
            self.selected_points = []

    def _highlight(self, pt):
        pt.setBrush(QBrush(QColor('green')))

    def _commit_line(self):
        p1 = self.selected_points[0]
        p2 = self.selected_points[1]
        x1, y1 = p1.rect().center().x(), p1.rect().center().y()
        x2, y2 = p2.rect().center().x(), p2.rect().center().y()
        line = QGraphicsLineItem(x1, y1, x2, y2)
        line.setPen(QPen(QColor('blue'), 2))
        self.canvas._scene.addItem(line)
        self.lines.append(line)
        dist = ((x1 - x2)**2 + (y1 - y2)**2)**0.5
        self.status_label.setText(f"Line between {p1.data(0)} and {p2.data(0)} length {dist:.2f}")
        p1.setBrush(QBrush(QColor('red')))
        p2.setBrush(QBrush(QColor('red')))

    def _commit_circle(self):
        center_item = self.selected_points[0]
        perimeter_item = self.selected_points[1]
        cx, cy = center_item.rect().center().x(), center_item.rect().center().y()
        px, py = perimeter_item.rect().center().x(), perimeter_item.rect().center().y()
        r = ((cx - px)**2 + (cy - py)**2)**0.5
        circle = QGraphicsEllipseItem(cx - r, cy - r, 2*r, 2*r)
        circle.setPen(QPen(QColor('magenta'), 2))
        self.canvas._scene.addItem(circle)
        self.circles.append(circle)
        self.status_label.setText(f"Circle with center {center_item.data(0)} and radius {r:.2f}")
        center_item.setBrush(QBrush(QColor('red')))
        perimeter_item.setBrush(QBrush(QColor('red')))

    def clear_all(self):
        self.canvas._scene.clear()
        self.points = []
        self.point_labels = []
        self.selected_points = []
        self.lines = []
        self.circles = []
        self.status_label.setText('Canvas cleared.')
