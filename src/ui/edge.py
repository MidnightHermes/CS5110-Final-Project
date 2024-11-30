import math
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPen, QPolygonF, QBrush
from PyQt6.QtWidgets import QGraphicsItemGroup, QGraphicsLineItem, QGraphicsPolygonItem

from ui.text_items import EdgeWeightTextItem


_weight = 1
def validateWeight(weight: str):
    global _weight

    try:
        _weight = float(weight)
    except ValueError:
        pass

class Edge(QGraphicsItemGroup):
    ARROW_HEIGHT = 25
    ARROW_WIDTH = 20

    _created = 0

    def __init__(self, originVertex, linkVertex, directed=True, weight=None, doOffset=False):
        super().__init__()

        global _weight
        if weight is None:
            weight = _weight
        else:
            _weight = weight

        self._originVertex = originVertex
        self._linkVertex = linkVertex

        pOrigin, pLink = self.getEndpoints()

        # Create an invisible line that is 4x as thick as the visible line
        #   to make it easier to grab the edge.
        self._visibleLine = QGraphicsLineItem(pOrigin.x(), pOrigin.y(), pLink.x(), pLink.y())
        self._visibleLine.setZValue(-2)

        self._linePen = QPen(Qt.GlobalColor.black)
        self._linePen.setWidth(3)
        self._visibleLine.setPen(self._linePen)

        self.addToGroup(self._visibleLine)

        # Then create a cosmetic (visible) line that is behind the invisible line.
        #   This is the line that the user sees.
        # Since this line is behind the invisible line, the user can only interact
        #   with the invisible line, as such this visible line is purely cosmetic.
        self._hitBox = self.createHitBox(pOrigin.x(), pOrigin.y(), pLink.x(), pLink.y())
        self.addToGroup(self._hitBox)

        self.stamp = Edge._created
        Edge._created += 1

        self._weightText = EdgeWeightTextItem(f'{_weight:g}', self._visibleLine, doOffset)
        self._weight = _weight

        # Handle arrowHead
        self._arrowHead = QGraphicsPolygonItem(self.getArrow(), self)
        self._arrowHead.setBrush(QBrush(Qt.GlobalColor.black))
        self._arrowHead.setZValue(-1)

        if directed:
            self.addToGroup(self._arrowHead)

    def getEndpoints(self):
        theta = self.theta

        cos = math.cos(theta)
        sin = math.sin(theta)

        cossin = QPointF(cos, sin)

        originOffs = self._originVertex.radius * cossin
        originRim = self._originVertex.center + originOffs

        linkOffs = self._linkVertex.radius * cossin
        linkRim = self._linkVertex.center - linkOffs

        return originRim, linkRim

    @property
    def dx(self):
        return self._linkVertex.x - self._originVertex.x

    @property
    def dy(self):
        return self._linkVertex.y - self._originVertex.y

    @property
    def theta(self):
        return math.atan2(self.dy, self.dx)

    @property
    def weight(self):
        return self._weight

    @property
    def pair(self):
        return (self._originVertex.label, self._linkVertex.label)

    def line(self):
        return self._visibleLine.line()

    def createHitBox(self, x1, y1, x2, y2) -> QGraphicsLineItem:
        hitBox = QGraphicsLineItem(x1, y1, x2, y2)
        hitBox.setZValue(-1)

        self._linePen.setWidth(12)
        hitBox.setPen(self._linePen)
        hitBox.setOpacity(0.0)

        return hitBox

    def getArrow(self) -> QPolygonF:
        theta = self.theta

        cos = math.cos(theta)
        sin = math.sin(theta)

        cossin = QPointF(cos, sin)

        tip = self.line().p2()

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
        origin, link = self.getEndpoints()
        self._visibleLine.setLine(origin.x(), origin.y(), link.x(), link.y())
        self._hitBox.setLine(origin.x(), origin.y(), link.x(), link.y())
        self._weightText.setPos(self._weightText.determinePosition())

        # Handle arrowHead
        self._arrowHead.setPolygon(self.getArrow())

    def remove(self, call_backend=True, caller=None):
        group = self.parentItem()

        self.scene().removeItem(self)
        group.removeFromGroup(self, call_backend)
       
        # need caller so we don't mutate a list that
        # is being iterated through in Vertex.remove()
        if caller is not self._originVertex:
            self._originVertex._edges.remove(self)
        if caller is not self._linkVertex:
            self._linkVertex._edges.remove(self)
