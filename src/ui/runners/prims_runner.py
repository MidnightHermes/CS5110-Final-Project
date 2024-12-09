from algorithms.prims import prims

class PrimsRunner:
    def __init__(self, scene):
        self.scene = scene
        self.graphScene = scene._graphScene
        self.graph = scene._graphScene.graph

    def run(self):
        try:
            self.mst = prims(self.graph)
        except:
            print(f"Failed to run Prim's Algorithm on {self.graph}\n", self.graph.edges(data=True), self.graph.nodes)
            return

        try:
            self.graphScene.clearGraph()
        except:
            print("Failed to clear graph")
            return

        try:
            self.graphScene.importGraph(self.mst)
        except:
            print(f"Failed to import MST {self.mst} into graph scene")
            return
