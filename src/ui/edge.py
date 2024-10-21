from PyQt6.QtWidgets import QGraphicsLineItem


class Edge(QGraphicsLineItem):
    _created = 0

    def __init__(self, originVertex, linkVertex):
        x1 = originVertex.x
        y1 = originVertex.y
        x2 = linkVertex.x
        y2 = linkVertex.y

        super().__init__(x1, y1, x2, y2)
        self.setZValue(-1)

        self.stamp = Edge._created
        Edge._created += 1

        self._originVertex = originVertex
        self._linkVertex = linkVertex
    
    def updatePosition(self):
        newX1 = self._originVertex.x
        newY1 = self._originVertex.y
        newX2 = self._linkVertex.x
        newY2 = self._linkVertex.y
        self.setLine(newX1, newY1, newX2, newY2)
