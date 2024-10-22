import math
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPen, QPolygonF, QBrush
from PyQt6.QtWidgets import QGraphicsLineItem, QGraphicsPolygonItem


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

class DirectedEdge(Edge):
    def __init__(self, originVertex, linkVertex):
        super().__init__(originVertex, linkVertex)
        
        self._arrowHead = QGraphicsPolygonItem(self.getArrowPos())
        self._arrowHead.setBrush(QBrush(Qt.GlobalColor.black))
        self._arrowHead.setZValue(-2)
    
    def getArrowPos(self):
        vertexRadius = 17.5
        arrowSize = 15

        linkPosX, linkPosY = (self._linkVertex.x, self._linkVertex.y)

        # Establish our starting points
        x1 = self._originVertex.x
        x2 = linkPosX
        y1 = self._originVertex.y
        y2 = linkPosY

        # Calculate the slope of the line intersecting our starting points
        dy = (y2 - y1)
        dx = (x2 - x1)
        m = dy / dx if dx != 0 else 0
        b = y1 - m * x1

        # Calculate the intersection points of our line and a perpendicular line
        m_inv = 1/m
        x_int = (y2 + (m_inv) * x2 + arrowSize - b) / (m + (m_inv)) - vertexRadius
        y_int = m * x_int + b

        # Determine the two points equidistant from the intersection points
        ux = 1 / math.sqrt(1 + (m_inv)**2)
        uy = (-m_inv) / math.sqrt(1 + (m_inv)**2)

        x1 = x_int + (arrowSize / 2) * ux
        y1 = y_int + (arrowSize / 2) * uy

        x2 = x_int - (arrowSize / 2) * ux
        y2 = y_int - (arrowSize / 2) * uy

        # Finally, create the two points making the corners of the arrow head
        p1 = QPointF(x1, y1)
        p2 = QPointF(x2, y2)
        # And the tip of the arrow head
        ux = 1 / math.sqrt(1 + m**2)
        uy = m / math.sqrt(1 + m**2)
        tipX = x_int + arrowSize * ux
        tipY = y_int + arrowSize * uy
        tip = QPointF(tipX, tipY)

        return QPolygonF([tip, p1, p2])
    
    def updatePosition(self):
        super().updatePosition()
        self._arrowHead.setPolygon(self.getArrowPos())
