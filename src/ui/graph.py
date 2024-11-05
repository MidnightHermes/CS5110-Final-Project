from typing import Optional
import networkx as nx
from PyQt6.QtWidgets import QGraphicsScene

from ui.edge import Edge
from ui.vertex import Vertex


class GraphScene:
    def __init__(self, scene: QGraphicsScene, graph: Optional[nx.Graph | nx.DiGraph]):
        self.scene = scene

        # List of vertices and edges created. Can possibly make it a set?
        self.scene.vertexList = []
        self.scene.edgeList = []

        self.scene._isSelectMode = False
        self.scene._isVertexMode = False
        self.scene._isEdgeMode = False
        self.scene._isWeighted = True
        self.scene._isDirected = True

        self.scene._originVertex = None

        if graph is not None:
            self.scene._graph = graph
            self.scene.importGraph(graph)
        else:
            self.scene._graph = nx.DiGraph()
    
    def setGraphType(self, graph_type: bool):
        self.scene._isDirected = graph_type
        if graph_type:
            self.scene._graph = self.scene._graph.to_directed()
        else:
            self.scene._graph = self.scene._graph.to_undirected()
        for edge in self.scene.edgeList:
            edge._arrowHead.setOpacity(1.0) if isinstance(self.scene._graph, nx.DiGraph) else edge._arrowHead.setOpacity(0.0)

    def setWeighted(self, weighted: bool):
        self.scene._isWeighted = weighted
        for edge in self.scene.edgeList:
            edge._weightText.setVisible(weighted)

    def importGraph(self, graph):
        # TODO: Find a better way to organize nodes when importing graph
        #   Currently just lines them up in order
        pos = (-Vertex.DIAMETER, Vertex.DIAMETER)
        for node in graph.nodes:
            pos = (pos[0] + 2 * Vertex.DIAMETER, pos[1])
            if pos[0] > self.scene.sceneRect().width():
                pos = (Vertex.DIAMETER, pos[1] + 2 * Vertex.DIAMETER)
            vertex = Vertex(*pos)
            vertex.label = node
            self.scene.vertexList.append(vertex)
            self.scene.addItem(vertex)

        for edge in graph.edges(graph, data=True):
            weight = edge[2]['weight']
            originVertex = next(vertex for vertex in self.scene.vertexList if vertex.label == edge[0])
            linkVertex = next(vertex for vertex in self.scene.vertexList if vertex.label == edge[1])
            edge = Edge(originVertex, linkVertex, self.scene._isDirected, weight)
            originVertex.addEdge(edge)
            linkVertex.addEdge(edge)
            self.scene.edgeList.append(edge)
            self.scene.addItem(edge)
    
    def addEdge(self, e):
        e.accept()

        nearest_vertex = self.scene.getItemUnderMouse(Vertex, self.scene.vertexList)
        if self.scene._originVertex is None:
            self.scene._originVertex = nearest_vertex
        else:
            # Catch case in which user clicks on empty space
            if (nearest_vertex is None or
                # or if user tries to connect a vertex to itself
                nearest_vertex == self.scene._originVertex or
                # or if user tries to connect originVertex to a vertex it is already connected to
                any(edge._linkVertex == nearest_vertex for edge in self.scene._originVertex._edges)):
                # Reset origin vertex anyways
                self.scene._originVertex = None
                return

            offset_weight = any(edge._linkVertex == self.scene._originVertex for edge in nearest_vertex._edges)
            
            edge_args = (self.scene._originVertex, nearest_vertex)
            edge = Edge(*edge_args, directed=self.scene._isWeighted, doOffset=offset_weight)

            self.scene._graph.add_edge(self.scene._originVertex.label, nearest_vertex.label, weight=edge.weight)

            self.scene._originVertex.addEdge(edge)
            nearest_vertex.addEdge(edge)
            self.scene.edgeList.append(edge)
            # Add edge _and_ cosmetic edge to scene
            self.scene.addItem(edge)
            self.scene._originVertex = None

    def addVertex(self, e):
        e.accept()

        x = e.scenePos().x()
        y = e.scenePos().y()

        vertex = Vertex(x, y)

        self.scene._graph.add_node(vertex.label)
        self.scene.vertexList.append(vertex)
        self.scene.addItem(vertex)

    def verticesMoved(self):
        for v in self.scene.vertexList:
            v.updateEdges()
