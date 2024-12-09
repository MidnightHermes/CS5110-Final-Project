import math
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtWidgets import QGraphicsEllipseItem
from PyQt6.QtGui import QBrush, QPen

from ui.text_items import TextItems


class Vertex(QGraphicsEllipseItem):
    DIAMETER = 50

    CUR_SELECTABLE = Qt.CursorShape.OpenHandCursor
    CUR_DRAG = Qt.CursorShape.ClosedHandCursor
    CUR_EDGE = Qt.CursorShape.PointingHandCursor

    _next_label = 0
    _created = 0

    def __init__(self, x, y, d=DIAMETER):
        # By default, x and y correspond to the top-left
        # corner of the rect bounding the circle.
        self._diameter = d
        cx = x - d/2
        cy = y - d/2

        self._edges = []

        super().__init__(cx, cy, d, d)

        self.stamp = Vertex._created
        Vertex._created += 1

        self.label = Vertex._next_label
        item = TextItems(str(Vertex._next_label), self)
        Vertex._next_label += 1

        # Define default colors
        self._outerColor = Qt.GlobalColor.black
        self._innerColor = Qt.GlobalColor.white

        # Pen describes the outline of a shape.
        self._circlePen = QPen(self.outerColor)
        self._circlePen.setWidth(3)

        # Brush describes the inside of a shape
        self._circleBrush = QBrush(self.innerColor)

        self.setPen(self._circlePen)
        self.setBrush(self._circleBrush)
    
    @property
    def outerColor(self) -> Qt.GlobalColor:
        return self._outerColor
    
    @property
    def innerColor(self) -> Qt.GlobalColor:
        return self._innerColor
    
    @outerColor.setter
    def outerColor(self, color: Qt.GlobalColor):
        self._circlePen.setColor(color)
        self.setPen(self._circlePen)
    
    @innerColor.setter
    def innerColor(self, color: Qt.GlobalColor):
        self._circleBrush.setColor(color)
        self.setBrush(self._circleBrush)

    @property
    def x(self) -> float:
        return self.sceneBoundingRect().center().x()
    
    @property
    def y(self) -> float:
        return self.sceneBoundingRect().center().y()

    @property
    def center(self) -> QPointF:
        return self.sceneBoundingRect().center()

    @property
    def diameter(self) -> int:
        return self._diameter

    @property
    def radius(self) -> float:
        return self._diameter / 2

    def getRadiusIntersect(self, other, r=None) -> QPointF:
        if r is None:
            r = self._diameter / 2

        dx = self.x - other.x
        dy = self.y - other.y

        theta = math.atan2(dy, dx)

        xOffs = r * math.cos(theta)
        yOffs = r * math.sin(theta)

        return QPointF(self.x - xOffs, self.y - yOffs)

    def addEdge(self, edge):
        self._edges.append(edge)

    def updateEdges(self):
        for edge in self._edges:
            edge.updatePosition()

    def isSelectable(self) -> Qt.CursorShape:
        return self.cursor() == Vertex.CUR_SELECTABLE

    def isDrag(self) -> Qt.CursorShape: # TODO: maybe make more rigorous
        return self.cursor() == Vertex.CUR_DRAG

    def remove(self):
        group = self.parentItem()

        self.scene().removeItem(self)
        group.removeFromGroup(self)

        for edge in self._edges:
            # need to specify that this object is removing the edge
            # so this edge list isn't modified
            edge.remove(False, self)

    def mousePressEvent(self, e):
        if (self.isSelectable() and
            e.button() == Qt.MouseButton.LeftButton):

            e.accept()

            self.setCursor(Vertex.CUR_DRAG)
        else:
            e.ignore()

    def mouseMoveEvent(self, e):
        super().mouseMoveEvent(e)

        self.scene()._graphScene.verticesMoved()

    def mouseReleaseEvent(self, e):
        if (self.isDrag() and  # If currently dragging in select mode
            e.button() == Qt.MouseButton.LeftButton):

            self.setCursor(Vertex.CUR_SELECTABLE)
            super().mouseReleaseEvent(e)
        else:
            e.ignore()
