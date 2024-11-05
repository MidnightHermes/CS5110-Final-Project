import math
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPen, QPolygonF, QBrush
from PyQt6.QtWidgets import QGraphicsLineItem, QGraphicsPolygonItem

from ui.text_items import EdgeWeightTextItem


_weight = 1
def validateWeight(weight: str):
    global _weight

    try:
        _weight = float(weight)
    except ValueError:
        pass

class Edge(QGraphicsLineItem):
    ARROW_HEIGHT = 25
    ARROW_WIDTH = 20

    _created = 0

    def __init__(self, originVertex, linkVertex, directed=True, weight=None, doOffset=False):
        if weight is None:
            weight = _weight

        x1 = originVertex.x
        y1 = originVertex.y
        x2 = linkVertex.x
        y2 = linkVertex.y

        # Create an invisible line that is 4x as thick as the visible line
        #   to make it easier to grab the edge.
        super().__init__(x1, y1, x2, y2)
        self.setZValue(-2)
        self._linePen = QPen(Qt.GlobalColor.black)
        self._linePen.setWidth(3)
        self.setPen(self._linePen)

        # Then create a cosmetic (visible) line that is behind the invisible line.
        #   This is the line that the user sees.
        # Since this line is behind the invisible line, the user can only interact
        #   with the invisible line, as such this visible line is purely cosmetic.
        self._hitBox = self.createHitBox(x1, y1, x2, y2)

        self.stamp = Edge._created
        Edge._created += 1

        self._weightText = EdgeWeightTextItem(f'{_weight:g}', self, doOffset)
        self._weight = _weight

        self._originVertex = originVertex
        self._linkVertex = linkVertex

        # Handle arrowHead
        self._arrowHead = QGraphicsPolygonItem(self.getArrow(), self)
        self._arrowHead.setBrush(QBrush(Qt.GlobalColor.black))
        self._arrowHead.setZValue(-1)

    @property
    def weight(self):
        return self._weight

    def createHitBox(self, x1, y1, x2, y2) -> QGraphicsLineItem:
        hitBox = QGraphicsLineItem(x1, y1, x2, y2)
        hitBox.setZValue(-1)

        self._linePen.setWidth(12)
        hitBox.setPen(self._linePen)
        hitBox.setOpacity(0.0)

        return hitBox

    def isUnderMouse(self) -> bool:
        return self._hitBox.isUnderMouse()

    def getArrow(self) -> QPolygonF:
        r = self._linkVertex.radius

        dx = self.line().dx()
        dy = self.line().dy()
    
        origin = self.line().p2()

        theta = math.atan2(dy, dx)

        cos = math.cos(theta)
        sin = math.sin(theta)

        cossin = QPointF(cos, sin)

        # Tip of the arrow head
        tipOffs = r * cossin
        tip = origin - tipOffs

        # Coordinate of where the base of the arrowhead
        # intersects the line
        baseOffs = self.ARROW_HEIGHT * cossin
        basePoint = tip - baseOffs

        # Calculate left and right wings of the arrowhead
        normal = theta + math.pi / 2
        wingOffs = (self.ARROW_WIDTH / 2) * QPointF(math.cos(normal), math.sin(normal))

        leftWing = basePoint - wingOffs
        rightWing = basePoint + wingOffs

        return QPolygonF([tip, leftWing, rightWing])

    def updatePosition(self):
        newX1 = self._originVertex.x
        newY1 = self._originVertex.y
        newX2 = self._linkVertex.x
        newY2 = self._linkVertex.y
        self.setLine(newX1, newY1, newX2, newY2)
        self._hitBox.setLine(newX1, newY1, newX2, newY2)
        self._weightText.setPos(self._weightText.determinePosition())

        # Handle arrowHead
        self._arrowHead.setPolygon(self.getArrow())

    def remove(self, call_backend=True, caller=None):
        scene = self.scene()

        if call_backend:
            fromLabel = self._originVertex.label
            toLabel = self._linkVertex.label
            scene._graph.remove_edge(fromLabel, toLabel)

        scene.edgeList.remove(self)

        scene.removeItem(self)
       
        # need caller so we don't mutate a list that
        # is being iterated through in Vertex.remove()
        if caller is not self._originVertex:
            self._originVertex._edges.remove(self)
        if caller is not self._linkVertex:
            self._linkVertex._edges.remove(self)
