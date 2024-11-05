from typing import Optional
import networkx as nx
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QGraphicsItem,
    QGraphicsScene,
)

from ui.vertex import Vertex
from ui.edge import Edge
from ui.graph import GraphScene


class Scene(QGraphicsScene):
    def __init__(self, x, y, width, height, graph: Optional[nx.Graph | nx.DiGraph]):
        super().__init__(x, y, width, height)

        self._isSelectMode = False
        self._isVertexMode = False
        self._isEdgeMode = False

        self._graphScene = GraphScene(graph)
        self.addItem(self._graphScene)

    def toggleSelectMode(self, b):
        self._isSelectMode = b

        # If select mode is enabled, make vertices selectable and movable.
        for v in self._graphScene.vertices:
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

        for v in self._graphScene.vertices:
            if b:
                v.setCursor(Vertex.CUR_EDGE)
            else:
                v.unsetCursor()

    def getItemUnderMouse(self, cls, itemList):
        underMouse = filter(cls.isUnderMouse, itemList)

        try:
            return max(underMouse, key=lambda i: i.stamp)
        except ValueError:
            return None
    
    # Calling this removeItemFromScene because removeItem is reserved by PyQt
    def removeItemFromScene(self, cls, e):
        e.accept()

        list = self._graphScene.vertices if cls == Vertex else self._graphScene.edges
        toBeRemoved = self.getItemUnderMouse(cls, list)

        if toBeRemoved is not None:
            toBeRemoved.remove()

    def mousePressEvent(self, e):
        if self._isSelectMode:
            super().mousePressEvent(e)  # propogate in order for select and drag to work
        elif self._isVertexMode:
            if e.button() == Qt.MouseButton.LeftButton:
                self._graphScene.addVertex(e)
            if e.button() == Qt.MouseButton.RightButton:
                self.removeItemFromScene(Vertex, e)
        elif self._isEdgeMode:
            if e.button() == Qt.MouseButton.LeftButton:
                self._graphScene.addEdge(e)
            if e.button() == Qt.MouseButton.RightButton:
                self.removeItemFromScene(Edge, e)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key.Key_P:
            print(self._graph.adj)
