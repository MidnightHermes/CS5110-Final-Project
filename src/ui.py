import sys

from PyQt6.QtCore import Qt
from PyQt6.QtCore import QPointF
from PyQt6.QtGui import QBrush, QPainter, QPen
from PyQt6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QGraphicsEllipseItem,
    QGraphicsItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsSimpleTextItem,
    QGraphicsView,
    QHBoxLayout,
    QMainWindow,
    QRadioButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)


next_label = 0
created = 0


class CenteredTextItem(QGraphicsSimpleTextItem):
    def __init__(self, text, parent, pos=None):
        super().__init__(text, parent)

        # By default, pos would be the top-left corner
        # of the textbox, so it needs to be corrected.

        if pos is None:
            pos = parent.boundingRect().center()

        rWidth = self.boundingRect().width()
        rHeight = self.boundingRect().height()
        true_pos = pos - QPointF(rWidth / 2, rHeight / 2)

        self.setPos(true_pos)
        self.setParentItem(parent)


class Vertex(QGraphicsEllipseItem):
    def __init__(self, x, y, d):
        # By default, x and y correspond to the top-left
        # corner of the rect bounding the circle.
        cx = x - d/2
        cy = y - d/2

        super().__init__(cx, cy, d, d)

        global created
        self.stamp = created
        created += 1

        global next_label
        self.label = next_label
        item = CenteredTextItem(str(next_label), self)
        next_label += 1



class Scene(QGraphicsScene):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)

        # Pen describes the outline of a shape.
        self._circlePen = QPen(Qt.GlobalColor.black)
        self._circlePen.setWidth(3)

        # Brush describes the inside of a shape
        self._circleBrush = QBrush(Qt.GlobalColor.white)

        # List of vertices created. Can possibly make it a set?
        self.vertexList = []

        self._isVertexMode = False

    def toggleSelectMode(self, b):
        # If select mode is enabled, make vertices selectable and movable.
        for v in self.vertexList:
            v.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, b)
            v.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, b)

    def toggleVertexMode(self, b):
        self._isVertexMode = b

    def mousePressEvent(self, e):
        if not self._isVertexMode:
            super().mousePressEvent(e)  # propogate in order for select and drag to work
            return

        # TODO: Delete vertices with right-click.
        # Might need to use contextMenuEvent for that.

        if e.button() == Qt.MouseButton.LeftButton:
            e.accept()
            x = e.scenePos().x()
            y = e.scenePos().y()

            vertex = Vertex(x, y, 50)
            vertex.setPen(self._circlePen)
            vertex.setBrush(self._circleBrush)
        
            self.vertexList.append(vertex)
            self.addItem(vertex)
        if e.button() == Qt.MouseButton.RightButton:
            underMouse = filter(lambda v: v.isUnderMouse(), self.vertexList)

            topVertex = max(underMouse, key=lambda v: v.stamp)

            self.removeItem(topVertex)

class Window(QWidget):
    def __init__(self):
        super().__init__()

        self.scene = Scene(0, 0, 800, 400)

        vbox = QVBoxLayout()

        self.initStateButtons(vbox)

        view = QGraphicsView(self.scene)
        view.setRenderHint(QPainter.RenderHint.Antialiasing)

        hbox = QHBoxLayout(self)
        hbox.addLayout(vbox)
        hbox.addWidget(view)

        self.setLayout(hbox)

    def initStateButtons(self, vbox):
        select_mode = QRadioButton("Select")
        select_mode.toggled.connect(self.scene.toggleSelectMode)
        vbox.addWidget(select_mode)

        select_mode.click()  # select mode is selected on startup

        vertex_mode = QRadioButton("Vertices")
        vertex_mode.toggled.connect(self.scene.toggleVertexMode)
        vbox.addWidget(vertex_mode)

        mode_group = QButtonGroup()
        mode_group.addButton(select_mode)
        mode_group.addButton(vertex_mode)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    w = Window()
    w.show()

    app.exec()

