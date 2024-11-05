from typing import Optional
import networkx as nx
from PyQt6.QtCore import QRectF
from PyQt6.QtWidgets import QGraphicsItem

from ui.edge import Edge
from ui.vertex import Vertex

class ItemGroup(QGraphicsItem):
    def __init__(self):
        super().__init__()

        self._items = []

    def addToGroup(self, item):
        item.setParentItem(self)
        self._items.append(item)

    def removeFromGroup(self, item):
        item.setParentItem(None)
        self._items.remove(item)

    def boundingRect(self):
        if len(self._items) == 0:
            return QRectF(0, 0, 0, 0)

        rect = self._items[0].boundingRect().translated(0, 0)

        for item in self._items:
            top = item.boundingRect().top()
            bottom = item.boundingRect().bottom()
            left = item.boundingRect().left()
            right = item.boundingRect().right()

            if rect.top() > top:
                rect.setTop(top)
            if rect.bottom() < bottom:
                rect.setBottom(bottom)
            if rect.left() > left:
                rect.setLeft(left)
            if rect.right() < right:
                rect.setRight(right)

        return rect

    def paint(self, painter, option, widget):
        pass


class GraphScene(ItemGroup):
    def __init__(self, graph: Optional[nx.Graph | nx.DiGraph]):
        super().__init__()

        # List of vertices and edges created. Can possibly make it a set?
        self._vertexList = []
        self._edgeList = []

        self._isWeighted = True
        self._isDirected = True

        self._originVertex = None

        if graph is not None:
            self._graph = graph
            self.importGraph(graph)
        else:
            self._graph = nx.DiGraph()

    @property
    def vertices(self):
        return self._vertexList
    
    @property
    def edges(self):
        return self._edgeList
    
    def setGraphType(self, graph_type: bool):
        self._isDirected = graph_type
        if graph_type:
            self._graph = self._graph.to_directed()
        else:
            self._graph = self._graph.to_undirected()
        for edge in self._edgeList:
            edge._arrowHead.setOpacity(1.0) if isinstance(self._graph, nx.DiGraph) else edge._arrowHead.setOpacity(0.0)

    def setWeighted(self, weighted: bool):
        self._isWeighted = weighted
        for edge in self._edgeList:
            edge._weightText.setVisible(weighted)

    def importGraph(self, graph):
        # TODO: Find a better way to organize nodes when importing graph
        #   Currently just lines them up in order
        pos = (-Vertex.DIAMETER, Vertex.DIAMETER)
        for node in graph.nodes:
            pos = (pos[0] + 2 * Vertex.DIAMETER, pos[1])
            if pos[0] > self.sceneRect().width():
                pos = (Vertex.DIAMETER, pos[1] + 2 * Vertex.DIAMETER)
            vertex = Vertex(*pos)
            vertex.label = node
            self._vertexList.append(vertex)
            self.addToGroup(vertex)

        for edge in graph.edges(graph, data=True):
            weight = edge[2]['weight']
            originVertex = next(vertex for vertex in self._vertexList if vertex.label == edge[0])
            linkVertex = next(vertex for vertex in self._vertexList if vertex.label == edge[1])
            edge = Edge(originVertex, linkVertex, self._isDirected, weight)
            originVertex.addEdge(edge)
            linkVertex.addEdge(edge)
            self._edgeList.append(edge)
            self.addToGroup(edge)
    
    def addEdge(self, e):
        e.accept()

        nearest_vertex = self.scene().getItemUnderMouse(Vertex, self._vertexList)
        if self._originVertex is None:
            self._originVertex = nearest_vertex
        else:
            # Catch case in which user clicks on empty space
            if (nearest_vertex is None or
                # or if user tries to connect a vertex to itself
                nearest_vertex == self._originVertex or
                # or if user tries to connect originVertex to a vertex it is already connected to
                any(edge._linkVertex == nearest_vertex for edge in self._originVertex._edges)):
                # Reset origin vertex anyways
                self._originVertex = None
                return

            offset_weight = any(edge._linkVertex == self._originVertex for edge in nearest_vertex._edges)
            
            edge_args = (self._originVertex, nearest_vertex)
            edge = Edge(*edge_args, directed=self._isWeighted, doOffset=offset_weight)

            self._graph.add_edge(self._originVertex.label, nearest_vertex.label, weight=edge.weight)

            self._originVertex.addEdge(edge)
            nearest_vertex.addEdge(edge)
            self._edgeList.append(edge)
            # Add edge _and_ cosmetic edge to scene
            self.addToGroup(edge)
            self._originVertex = None

    def addVertex(self, e):
        e.accept()

        x = e.scenePos().x()
        y = e.scenePos().y()

        vertex = Vertex(x, y)

        self._graph.add_node(vertex.label)
        self._vertexList.append(vertex)
        self.addToGroup(vertex)

    def verticesMoved(self):
        for v in self._vertexList:
            v.updateEdges()
