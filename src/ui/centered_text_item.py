from PyQt6.QtCore import QPointF
from PyQt6.QtWidgets import QGraphicsSimpleTextItem

class CenteredTextItem(QGraphicsSimpleTextItem):
    def __init__(self, text, parent, pos=None):
        super().__init__(text, parent)
        self._parent = parent
        self._pos = pos

        self.setPos(self.determinePosition())
        self.setParentItem(self._parent)

    def determinePosition(self):
        # By default, pos would be the top-left corner
        # of the textbox, so it needs to be corrected.

        if self._pos is None:
            self._pos = self._parent.sceneBoundingRect().center()

        rWidth = self.sceneBoundingRect().width()
        rHeight = self.sceneBoundingRect().height()
        return self._pos - QPointF(rWidth / 2, rHeight / 2)

class EdgeWeightTextItem(CenteredTextItem):
    def __init__(self, text, parent, pos=None):
        self._parent = parent
        self._pos = pos

        super().__init__(text, parent, self.determinePosition())
    
    def determinePosition(self):
        dx = self._parent.line().dx()
        dy = self._parent.line().dy()
        slope = dy / dx if dx != 0 else 0
        b = self._parent.line().p2().y() - slope * self._parent.line().p2().x()

        if b < 0 or slope < 0:
            direction = -1
        else:
            direction = 1

        return self._parent.line().center() + (direction * QPointF(10, 10))
