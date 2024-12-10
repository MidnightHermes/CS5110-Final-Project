import networkx as nx
from PyQt6.QtCore import Qt

from algorithms.girvan_newman import girvan_newman


class GirvanNewmanRunner:
    def __init__(self, scene):
        self.scene = scene
        self.graphScene = scene._graphScene
        self.graph = scene._graphScene.graph

    def run(self):
        self.communities, self.edges = next(girvan_newman(self.graph.copy(), return_extra_info=True))

        colors = [Qt.GlobalColor.red, Qt.GlobalColor.blue, Qt.GlobalColor.green, Qt.GlobalColor.magenta]
        # Don't add edges that were drawn in the previous community
        previous_communities = []
        for i, community in enumerate(self.communities):
            new_edges = [(edge[0], edge[1]) for edge in self.edges if (edge[0] not in previous_communities and edge[1] not in previous_communities) and (edge[0] in community and edge[1] in community)]
            print(new_edges)
            self.graphScene.colorEdges(new_edges, colors[i])
            previous_communities.extend(community)
            self.graphScene.colorVertices(community, colors[i])
