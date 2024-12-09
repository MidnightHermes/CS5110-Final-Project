from algorithms.max_clique import ramsey

from PyQt6.QtCore import Qt

class MaxCliqueRunner:
    def __init__(self, scene):
        self.scene = scene

    def run(self):
        c, ind = ramsey(self.scene._graphScene.graph)
        print(c, ind)

        self.scene._graphScene.colorVertices(c, Qt.GlobalColor.darkCyan)

        clique_edges = []
        c = sorted(c)
        for i in range(len(c) - 1):
            for j in range(i + 1, len(c)):
                clique_edges.append((c[i], c[j]))

        self.scene._graphScene.colorEdges(clique_edges, Qt.GlobalColor.darkCyan)

        self.scene._graphScene.colorVertices(ind, Qt.GlobalColor.green)

        self.scene._resetColorOnClick = True
