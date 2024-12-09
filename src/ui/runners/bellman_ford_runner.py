from algorithms.bellman import bellman_ford, NegativeCycleException

from PyQt6.QtCore import Qt

class BellmanFordRunner:
    def __init__(self, scene):
        self.scene = scene

    def assignMouse(self):
        self.scene._needBFSource = True
        self.scene._bellmanHook = self.run

    def run(self, vertex):
        self.scene._needBFSource = False
        self.scene._bellmanHook = None

        try:
            _, preds = bellman_ford(self.scene._graphScene.graph, vertex)

            edges = []

            for v, p in preds.items():
                if p is None:
                    continue

                pair = (p, v)
                edges.append(pair)

            self.scene._graphScene.colorEdges(edges, Qt.GlobalColor.magenta)
            
        except NegativeCycleException as nce:
            self.scene._graphScene.colorEdges(nce.edges, Qt.GlobalColor.red)
            self.scene._graphScene.colorVertices(nce.cycle, Qt.GlobalColor.red)
        
        self.scene._resetColorOnClick = True
