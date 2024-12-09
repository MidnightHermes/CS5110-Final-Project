from algorithms.prims import prims
from PyQt6.QtCore import Qt


class PrimsRunner:
    def __init__(self, scene):
        self.scene = scene
        self.graphScene = scene._graphScene
        self.graph = scene._graphScene.graph

    def run(self):
        if self.graph.is_directed():
            self.graph = self.graph.to_undirected()
        if self.graph.number_of_nodes() == 0:
            return

        mst = prims(self.graph.copy())
        mst_edges = mst.edges()

        self.scene._graphScene.colorEdges(mst_edges, Qt.GlobalColor.darkRed)

        self.scene._resetColorOnClick = True
