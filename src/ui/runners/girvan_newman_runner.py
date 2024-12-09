import networkx as nx
from PyQt6.QtCore import Qt

from algorithms.girvan_newman import girvan_newman


class GirvanNewmanRunner:
    def __init__(self, scene):
        self.scene = scene
        self.graphScene = scene._graphScene
        self.graph = scene._graphScene.graph

    def run(self):
        self.communities, self.edges = next(girvan_newman(self.graph, return_extra_info=True))
        # Make a copy because NetworkX passes by reference instead of value (very annoying)
        self.edges = list(self.edges).copy()

        self.graphScene.clearGraph()

        colors = [Qt.GlobalColor.red, Qt.GlobalColor.blue]
        # Don't add edges that were drawn in the previous community
        previous_communities = []
        final_graph = nx.Graph()
        for i, community in enumerate(self.communities):
            G = nx.Graph()

            new_edges = [edge for edge in self.edges if (edge[0] not in previous_communities and edge[1] not in previous_communities) and (edge[0] in community and edge[1] in community)]
            previous_communities.extend(community)
            print(len(new_edges))
            G.add_edges_from(new_edges)

            print(community, G.nodes, '\n\n', previous_communities, '\n\n\n\n')
            final_graph = nx.compose(final_graph, G)
        
        self.graphScene.importGraph(final_graph)
        for i, community in enumerate(self.communities):
            self.graphScene.colorVertices(community, colors[i])
