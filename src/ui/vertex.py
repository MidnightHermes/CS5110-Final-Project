import math
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtWidgets import QGraphicsEllipseItem

from ui.centered_text_item import CenteredTextItem


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
        item = CenteredTextItem(str(Vertex._next_label), self)
        Vertex._next_label += 1

    @property
    def x(self):
        return self.sceneBoundingRect().center().x()
    
    @property
    def y(self):
        return self.sceneBoundingRect().center().y()

    @property
    def diameter(self):
        return self._diameteer

    @property
    def radius(self):
        return self._diameter / 2

    def getRadiusIntersect(self, other, r=None):
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
