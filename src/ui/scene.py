from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QPen
from PyQt6.QtWidgets import (
    QGraphicsItem,
    QGraphicsScene,
)
from vertex import Vertex
from edge import Edge


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
        e.accept()

        x = e.scenePos().x()
        y = e.scenePos().y()

        nearest_vertex = self.getVertexUnderMouse()
        if self._originVertex is None:
            self._originVertex = nearest_vertex
        else:
            # Catch case in which user clicks on empty space
            if (nearest_vertex is None or
                # or if user tries to connect a vertex to itself
                nearest_vertex == self._originVertex or
                # or if user tries to connect originVertex to a vertex it is already connected to
                any(edge._linkVertex == nearest_vertex for edge in self._originVertex._edges) or
                # or if user tries to connect a vertex to the originVertex that is already connected to it
                any(edge._linkVertex == self._originVertex for edge in nearest_vertex._edges)):
                print("Resetting vertex")
                # Reset origin vertex anyways
                self._originVertex = None
                return
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
