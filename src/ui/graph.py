from typing import Optional
import networkx as nx
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QTransform
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
    
    def translate(self, dx, dy):
        transform = QTransform()

        transform.translate(dx, dy)

        self.setTransform(transform, combine=True)

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

        self._coloredVertices = {}
        self._coloredEdges = {}

    @property
    def graph(self):
        return self._graph

    @property
    def vertices(self):
        return self._vertexList
    
    @property
    def edges(self):
        return self._edgeList
    
    def clearGraph(self):
        self._vertexList.clear()
        self._edgeList.clear()
        self._graph.clear()
        remaining = self.scene().items(self.scene().sceneRect())
        for item in remaining:
            if isinstance(item, Vertex) or isinstance(item, Edge):
                self.scene().removeItem(item)
        self._originVertex = None
        Vertex._next_label = 0
    
    def setGraphType(self, graph_type: bool):
        self._isDirected = graph_type
        if graph_type:
            self._graph = self._graph.to_directed()
        else:
            self._graph = self._graph.to_undirected()
        for edge in self._edgeList:
            edge._arrowHead.setOpacity(1.0) if self._isDirected else edge._arrowHead.setOpacity(0.0)

    def setWeighted(self, weighted: bool):
        self._isWeighted = weighted
        for edge in self._edgeList:
            edge._weightText.setVisible(weighted)

    def importGraph(self, graph):
        # Use networkx's shell layout to position vertices
        positions = nx.shell_layout(graph)
        # Then normalize the positions to match PyQt6 coordinate system
        min_x = min(x for x, y in positions.values())
        min_y = min(y for x, y in positions.values())
        # Finally, update the backend graph object to include the new graph
        self._graph = nx.disjoint_union(self._graph, graph)
        for node, (x, y) in positions.items():
            # And scale the positions to fit the size of the scene
            vertex = Vertex((x - min_x * 2) * 200, (y - min_y * 1.5) * 150)
            vertex.label = node
            self._vertexList.append(vertex)
            self.addToGroup(vertex)

        for edge in graph.edges(graph, data=True):
            try:
                weight = edge[2]['weight']
            except KeyError:
                weight = None
            originVertex = next(vertex for vertex in self._vertexList if vertex.label == edge[0])
            linkVertex = next(vertex for vertex in self._vertexList if vertex.label == edge[1])
            offset_weight = self.doOffset(originVertex, linkVertex)
            edge = Edge(originVertex, linkVertex, self._isDirected, weight, offset_weight)
            originVertex.addEdge(edge)
            linkVertex.addEdge(edge)
            self._edgeList.append(edge)
            self.addToGroup(edge)
        
        if self.scene()._isSelectMode:
            self.scene().toggleSelectMode(True)
        elif self.scene()._isVertexMode:
            self.scene().toggleVertexMode(True)
        elif self.scene()._isEdgeMode:
            self.scene().toggleEdgeMode(True)
    
    def doOffset(self, originVertex, linkVertex):
        return any(edge._linkVertex == originVertex for edge in linkVertex._edges)
    
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

            offset_weight = self.doOffset(self._originVertex, nearest_vertex)
            
            edge_args = (self._originVertex, nearest_vertex)
            edge = Edge(*edge_args, directed=self._isDirected, doOffset=offset_weight)

            self._graph.add_edge(self._originVertex.label, nearest_vertex.label, weight=edge.weight)

            self._originVertex.addEdge(edge)
            nearest_vertex.addEdge(edge)
            self._edgeList.append(edge)
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

    def removeFromGroup(self, item, call_backend=True):
        super().removeFromGroup(item)

        if isinstance(item, Vertex):
            self._vertexList.remove(item)
            if call_backend:
                self._graph.remove_node(item.label)
        else:
            assert(isinstance(item, Edge))
            self._edgeList.remove(item)
            
            if call_backend:
                self._graph.remove_edge(*item.pair)

    def colorVertices(self, vertices, color):
        toColor = []

        for query in vertices:
            # terrible no good linear search
            for v in self._vertexList:
                if v.label == query:
                    toColor.append(v)

        for v in toColor:
            v.innerColor = color
        
        vs = set(toColor)
        self._coloredVertices |= vs

    def colorEdges(self, edges, color):
        toColor = []

        for query in edges:
            # that linear search again
            for e in self._edgeList:
                if e.pair == query or (not self._isDirected and tuple(reversed(e.pair)) == query):
                    toColor.append(e)

        for e in toColor:
            e.color = color

        es = set(toColor)
        self._coloredEdges |= es

    def clearColors(self):
        for v in self._coloredVertices:
            v.innerColor = Qt.GlobalColor.white
            v.outerColor = Qt.GlobalColor.black

        for e in self._coloredEdges:
            e.color = Qt.GlobalColor.black
