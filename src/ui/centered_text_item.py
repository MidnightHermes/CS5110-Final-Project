from PyQt6.QtCore import QPointF
from PyQt6.QtWidgets import QGraphicsSimpleTextItem

class CenteredTextItem(QGraphicsSimpleTextItem):
    def __init__(self, text, parent, pos=None):
        super().__init__(text, parent)

        # By default, pos would be the top-left corner
        # of the textbox, so it needs to be corrected.

        if pos is None:
            pos = parent.sceneBoundingRect().center()

        rWidth = self.sceneBoundingRect().width()
        rHeight = self.sceneBoundingRect().height()
        true_pos = pos - QPointF(rWidth / 2, rHeight / 2)

        self.setPos(true_pos)
        self.setParentItem(parent)
