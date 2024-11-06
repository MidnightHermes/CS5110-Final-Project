import math
from PyQt6.QtCore import QPointF
from PyQt6.QtWidgets import QGraphicsSimpleTextItem


class TextItems(QGraphicsSimpleTextItem):
    def __init__(self, text, parent, pos=None):
        super().__init__(text, parent)
        self._pos = pos

        self.setPos(self.determinePosition())

    def determinePosition(self) -> QPointF:
        # By default, pos would be the top-left corner
        # of the textbox, so it needs to be corrected.

        if self._pos is None:
            self._pos = self.parentItem().sceneBoundingRect().center()

        rWidth = self.sceneBoundingRect().width()
        rHeight = self.sceneBoundingRect().height()
        return self._pos - QPointF(rWidth / 2, rHeight / 2)

class EdgeWeightTextItem(TextItems):
    def __init__(self, text, parent, doOffset: bool, pos=None):
        self._offsetWeight = doOffset

        super().__init__(text, parent)
    
    def determinePosition(self) -> QPointF:
        dx = self.parentItem().line().dx()
        dy = self.parentItem().line().dy()
        theta = math.atan2(dy, dx)
        normal = theta + math.pi / 2
        offset = 10 * QPointF(math.cos(normal), math.sin(normal))
        basePoint = self.parentItem().line().center()

        if self._offsetWeight:
            # TODO: Make offset calculation more robust for reflexive edges
            offset = -offset

        return basePoint + offset if theta < 0.33 * math.pi and theta > -0.67 * math.pi else basePoint - offset
