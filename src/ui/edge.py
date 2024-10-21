from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPen
from PyQt6.QtWidgets import QGraphicsLineItem


class Edge(QGraphicsLineItem):
    _created = 0

    def __init__(self, originVertex, linkVertex):
        x1 = originVertex.x
        y1 = originVertex.y
        x2 = linkVertex.x
        y2 = linkVertex.y

        # Create an invisible line that is 4x as thick as the visible line
        #   to make it easier to grab the edge.
        super().__init__(x1, y1, x2, y2)
        self.setZValue(-1)
        linePen = QPen(Qt.GlobalColor.black)
        linePen.setWidth(12)
        self.setPen(linePen)
        self.setOpacity(0.0)

        # Then create a cosmetic (visible) line that is behind the invisible line.
        #   This is the line that the user sees.
        # Since this line is behind the invisible line, the user can only interact
        #   with the invisible line, as such this visible line is purely cosmetic.
        self._cosmeticLine = self.createCosmeticLine(x1, y1, x2, y2)

        self.stamp = Edge._created
        Edge._created += 1

        self._originVertex = originVertex
        self._linkVertex = linkVertex
    
    def createCosmeticLine(self, x1, y1, x2, y2):
        cosmeticLine = QGraphicsLineItem(x1, y1, x2, y2)
        cosmeticLine.setZValue(-2)
        
        linePen = QPen(Qt.GlobalColor.black)
        linePen.setWidth(3)
        cosmeticLine.setPen(linePen)

        return cosmeticLine
    
    def updatePosition(self):
        newX1 = self._originVertex.x
        newY1 = self._originVertex.y
        newX2 = self._linkVertex.x
        newY2 = self._linkVertex.y
        self.setLine(newX1, newY1, newX2, newY2)
        self._cosmeticLine.setLine(newX1, newY1, newX2, newY2)
