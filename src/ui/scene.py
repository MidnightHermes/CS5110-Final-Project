from typing import Optional
import networkx as nx
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QTransform
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

        self._dragging = False # True if scene is in a scene dragging state
        self._dragMousePos = None

        self._needBFSource = False
        self._bellmanHook = None

        self._resetColorOnClick = False

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
        
    def getVertexUnderMouse(self):
        return self.getItemUnderMouse(Vertex, self._graphScene.vertices)
    
    # Calling this removeItemFromScene because removeItem is reserved by PyQt
    def removeItemFromScene(self, cls, e):
        e.accept()

        list = self._graphScene.vertices if cls == Vertex else self._graphScene.edges
        toBeRemoved = self.getItemUnderMouse(cls, list)

        if toBeRemoved is not None:
            toBeRemoved.remove()

    def mousePressEvent(self, e):
        if self._resetColorOnClick:
            self._graphScene.clearColors()

        if self._needBFSource:
            v = self.getVertexUnderMouse()
            if v is not None:
                self._bellmanHook(v.label)

            return None

        if self._isSelectMode:
            if e.button() == Qt.MouseButton.LeftButton and self.getVertexUnderMouse() is None:
                if not e.modifiers() & Qt.KeyboardModifier.ControlModifier:
                    self.clearSelection() # Un-select selected vertices if CTRL isn't being held down

                self._dragging = True
                self._dragMousePos = e.scenePos() # Store initial mouse position
            else:
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

    def mouseReleaseEvent(self, e):
        if self._dragging and e.button() == Qt.MouseButton.LeftButton:
            self._dragging = False
        else:
            super().mouseReleaseEvent(e)

    def mouseMoveEvent(self, e):
        if False and self._dragging: # disable dragging because incredibly scuffed
            # How much mouse has moved since last time
            d = e.scenePos() - self._dragMousePos

            # Current position will be the next old position
            self._dragMousePos = e.scenePos()

            self._graphScene.translate(d.x(), d.y())
        else:
            super().mouseMoveEvent(e)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key.Key_P:
            print(self._graphScene.graph.adj)

    def wheelEvent(self, e):
        delta = e.delta() / (360 * 8)

        view = self.views()[0]

        scale = 1 + delta

        view.scale(scale, scale)
