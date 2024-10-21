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
    QGraphicsLineItem,
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
            pos = parent.sceneBoundingRect().center()

        rWidth = self.sceneBoundingRect().width()
        rHeight = self.sceneBoundingRect().height()
        true_pos = pos - QPointF(rWidth / 2, rHeight / 2)

        self.setPos(true_pos)
        self.setParentItem(parent)


class Edge(QGraphicsLineItem):
    def __init__(self, originVertex, linkVertex):
        x1 = originVertex.x
        y1 = originVertex.y
        x2 = linkVertex.x
        y2 = linkVertex.y

        super().__init__(x1, y1, x2, y2)
        self.setZValue(-1)

        self._originVertex = originVertex
        self._linkVertex = linkVertex
    
    def updatePosition(self):
        newX1 = self._originVertex.x
        newY1 = self._originVertex.y
        newX2 = self._linkVertex.x
        newY2 = self._linkVertex.y
        self.setLine(newX1, newY1, newX2, newY2)


class Vertex(QGraphicsEllipseItem):
    CUR_SELECTABLE = Qt.CursorShape.OpenHandCursor
    CUR_DRAG = Qt.CursorShape.ClosedHandCursor
    CUR_EDGE = Qt.CursorShape.PointingHandCursor

    def __init__(self, x, y, d):
        # By default, x and y correspond to the top-left
        # corner of the rect bounding the circle.
        cx = x - d/2
        cy = y - d/2

        self._edges = []

        super().__init__(cx, cy, d, d)

        global created
        self.stamp = created
        created += 1

        global next_label
        self.label = next_label
        item = CenteredTextItem(str(next_label), self)
        next_label += 1

    @property
    def x(self):
        return self.sceneBoundingRect().center().x()
    
    @property
    def y(self):
        return self.sceneBoundingRect().center().y()

    def addEdge(self, edge):
        self._edges.append(edge)

    def updateEdges(self):
        for edge in self._edges:
            edge.updatePosition()

    def isSelectable(self):
        return self.cursor() == Vertex.CUR_SELECTABLE

    def isDrag(self): # TODO: maybe make more rigorous
        return self.cursor() == Vertex.CUR_DRAG

    def mousePressEvent(self, e):
        if (self.isSelectable() and
            e.button() == Qt.MouseButton.LeftButton):

            e.accept()

            self.setCursor(Vertex.CUR_DRAG)
        else:
            e.ignore()

    def mouseMoveEvent(self, e):
        super().mouseMoveEvent(e)

        self.scene().verticesMoved()

    def mouseReleaseEvent(self, e):
        if (self.isDrag() and  # If currently dragging in select mode
            e.button() == Qt.MouseButton.LeftButton):

            self.setCursor(Vertex.CUR_SELECTABLE)
            super().mouseReleaseEvent(e)
        else:
            e.ignore()

class Scene(QGraphicsScene):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)

        # Pen describes the outline of a shape.
        self._circlePen = QPen(Qt.GlobalColor.black)
        self._circlePen.setWidth(3)

        # Brush describes the inside of a shape
        self._circleBrush = QBrush(Qt.GlobalColor.white)

        # List of vertices and edges created. Can possibly make it a set?
        self.vertexList = []
        self.edgeList = []

        self._isSelectMode = False
        self._isVertexMode = False
        self._isEdgeMode = False

        self._originVertex = None

    def toggleSelectMode(self, b):
        self._isSelectMode = b

        # If select mode is enabled, make vertices selectable and movable.
        for v in self.vertexList:
            v.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, b)
            v.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, b)
            
            if b:
                v.setCursor(Vertex.CUR_SELECTABLE)
            else:
                v.unsetCursor()

    def toggleVertexMode(self, b):
        self._isVertexMode = b

    def toggleEdgeMode(self, b):
        self._isEdgeMode = b
        # TODO: make vertices bubble out a little when hovered over

        for v in self.vertexList:
            if b:
                v.setCursor(Vertex.CUR_EDGE)
            else:
                v.unsetCursor()

    def getVertexUnderMouse(self):
        underMouse = filter(Vertex.isUnderMouse, self.vertexList)

        try:
            return max(underMouse, key=lambda v: v.stamp)
        except ValueError:  # If underMouse is an empty list
            return None
    
    def addEdge(self, e):
        # TODO: Do not draw an edge between two vertices that already have an edge drawn between them

        e.accept()

        x = e.scenePos().x()
        y = e.scenePos().y()

        nearest_vertex = self.getVertexUnderMouse()
        if self._originVertex is None:
            self._originVertex = nearest_vertex
        else:
            edge = Edge(self._originVertex, nearest_vertex)
            edge.setPen(self._circlePen)

            self._originVertex.addEdge(edge)
            nearest_vertex.addEdge(edge)
            self.edgeList.append(edge)
            self.addItem(edge)
            self._originVertex = None

    def removeEdge(self, e):
        e.accept()

        toBeRemoved = self.getEdgeUnderMouse() # TODO: Implement getEdgeUnderMouse

        if toBeRemoved is not None:
            self.removeItem(toBeRemoved)
            self.edgeList.remove(toBeRemoved)

    def addVertex(self, e):
        e.accept()

        x = e.scenePos().x()
        y = e.scenePos().y()

        vertex = Vertex(x, y, 50)
        vertex.setPen(self._circlePen)
        vertex.setBrush(self._circleBrush)
        
        self.vertexList.append(vertex)
        self.addItem(vertex)

    def removeVertex(self, e):
        e.accept()

        toBeRemoved = self.getVertexUnderMouse()
            
        if toBeRemoved is not None:
            self.removeItem(toBeRemoved)
            self.vertexList.remove(toBeRemoved)

    def verticesMoved(self):
        for v in self.vertexList:
            v.updateEdges()

    def mousePressEvent(self, e):
        if self._isSelectMode:
            super().mousePressEvent(e)  # propogate in order for select and drag to work
        elif self._isVertexMode:
            if e.button() == Qt.MouseButton.LeftButton:
                self.addVertex(e)
            if e.button() == Qt.MouseButton.RightButton:
                self.removeVertex(e)
        elif self._isEdgeMode:
            if e.button() == Qt.MouseButton.LeftButton:
                self.addEdge(e)
            if e.button() == Qt.MouseButton.RightButton:
                self.removeEdge(e)

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

        edge_mode = QRadioButton("Edges")
        edge_mode.toggled.connect(self.scene.toggleEdgeMode)
        vbox.addWidget(edge_mode)

        mode_group = QButtonGroup()
        mode_group.addButton(select_mode)
        mode_group.addButton(vertex_mode)
        mode_group.addButton(edge_mode)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    w = Window()
    w.show()

    app.exec()

