import networkx as nx
from PyQt6.QtCore import Qt, QEventLoop, QPoint
from PyQt6.QtGui import QIntValidator
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QLineEdit,
    QListView,
    QPushButton,
    QSizePolicy,
    QLabel,
    QDialogButtonBox,
)


class RunAlgPopup(QWidget):
    """
    Based on https://stackoverflow.com/questions/67029993/pyqt-creating-a-popup-in-the-window
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setAutoFillBackground(True)
        self.setStyleSheet('''
            Popup {
                background: rgba(64, 64, 64, 64);
            }
            QWidget#container {
                border: 2px solid darkGray;
                border-radius: 4px;
                background: rgb(64, 64, 64);
            }
            QWidget#container > QLabel {
                color: white;
            }
            QLabel#title {
                font-size: 20pt;
            }
            QPushButton#close {
                color: white;
                font-weight: bold;
                background: none;
                border: 1px solid gray;
            }
        ''')
        fullLayout = QVBoxLayout(self)
        self.container = QWidget(autoFillBackground=True, objectName='container')
        fullLayout.addWidget(self.container, alignment=Qt.AlignmentFlag.AlignCenter)
        self.container.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        buttonSize = self.fontMetrics().height()
        self.closeButton = QPushButton('x', self.container, objectName='close')
        self.closeButton.setFixedSize(buttonSize, buttonSize)
        self.closeButton.clicked.connect(self.reject)
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(buttonSize * 2, buttonSize, buttonSize * 2, buttonSize)
        title = QLabel('Select a graph generation method', objectName='title', alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)



        from ui.runners.prims_runner import PrimsRunner
        self.prims_runner = PrimsRunner(parent.scene)
        self.prims_button = QPushButton("Prim's Algorithm")
        self.prims_button.clicked.connect(self.accept)
        self.prims_button.clicked.connect(self.prims_runner.run)
        layout.addWidget(self.prims_button)

        from ui.runners.girvan_newman_runner import GirvanNewmanRunner
        self.girvan_newman_runner = GirvanNewmanRunner(parent.scene)
        self.girvan_newman_button = QPushButton("Girvan-Newman Algorithm")
        self.girvan_newman_button.clicked.connect(self.accept)
        self.girvan_newman_button.clicked.connect(self.girvan_newman_runner.run)
        layout.addWidget(self.girvan_newman_button)

        from ui.runners.bellman_ford_runner import BellmanFordRunner
        self.bellman_ford_runner = BellmanFordRunner(parent.scene)
        self.bellman_ford_button = QPushButton("Bellman-Ford Algorithm")
        self.bellman_ford_button.clicked.connect(self.accept)
        self.bellman_ford_button.clicked.connect(self.bellman_ford_runner.run)
        layout.addWidget(self.bellman_ford_button)

        from ui.runners.max_clique_runner import MaxCliqueRunner
        self.max_clique_runner = MaxCliqueRunner(parent.scene)
        self.max_clique_button = QPushButton("Max Clique Approximation")
        self.max_clique_button.clicked.connect(self.accept)
        self.max_clique_button.clicked.connect(self.max_clique_runner.run)
        layout.addWidget(self.max_clique_button)



        parent.installEventFilter(self)
        self.loop = QEventLoop(self)

    def accept(self):
        self.loop.exit(True)

    def reject(self):
        self.loop.exit(False)

    def close(self):
        self.loop.quit()

    def showEvent(self, event):
        self.setGeometry(self.parent().rect())

    def resizeEvent(self, event):
        r = self.closeButton.rect()
        r.moveTopRight(self.container.rect().topRight() + QPoint(-5, 5))
        self.closeButton.setGeometry(r)

    def eventFilter(self, source, event):
        if event.type() == event.Type.Resize:
            self.setGeometry(source.rect())
        return super().eventFilter(source, event)

    def exec_(self):
        self.show()
        self.raise_()
        res = self.loop.exec()
        self.hide()
        return res
