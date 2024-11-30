from typing import Optional, Union
import networkx as nx
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QDoubleValidator
from PyQt6.QtWidgets import (
    QButtonGroup,
    QGraphicsView,
    QHBoxLayout,
    QRadioButton,
    QVBoxLayout,
    QWidget,
    QLineEdit,
    QCheckBox,
)

from ui.scene import Scene
from ui.edge import validateWeight


MAX_WEIGHT_INPUT = 1000
MIN_WEIGHT_INPUT = -1000


class Window(QWidget):
    def __init__(self, graph: Optional[Union[nx.Graph, nx.DiGraph]]=None):

        super().__init__()

        self.scene = Scene(0, 0, 800, 400, graph)

        vbox = QVBoxLayout()

        self.initGraphTypeButtons(vbox)
        self.initStateButtons(vbox)

        if graph is not None:
            self.directed_toggle.setChecked(isinstance(graph, nx.DiGraph))

        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        hbox = QHBoxLayout(self)
        hbox.addLayout(vbox)
        hbox.addWidget(self.view)

        self.setLayout(hbox)
    
    def initGraphTypeButtons(self, vbox):
        vbox_top = QVBoxLayout()

        self.directed_toggle = QCheckBox("Directed")

        vbox_top.addWidget(self.directed_toggle)

        self.directed_toggle.setChecked(True)  # Default to undirected mode

        self.directed_toggle.clicked.connect(self.confirmGraphType)

        vbox.addLayout(vbox_top)
    
    def confirmGraphType(self):
        self.scene._graphScene.setGraphType(self.directed_toggle.isChecked())

    def initStateButtons(self, vbox):
        self.select_mode = QRadioButton("Select")
        self.select_mode.toggled.connect(self.scene.toggleSelectMode)
        self.select_mode.click()  # select mode is selected on startup
        vbox.addWidget(self.select_mode)

        self.vertex_mode = QRadioButton("Vertices")
        self.vertex_mode.toggled.connect(self.scene.toggleVertexMode)
        vbox.addWidget(self.vertex_mode)

        self.edge_mode = QRadioButton("Edges")
        self.edge_mode.toggled.connect(self.scene.toggleEdgeMode)
        vbox.addWidget(self.edge_mode)

        weight_hbox = QHBoxLayout()
        weight_input = QLineEdit("")
        weight_input.setPlaceholderText("Enter weight")
        weight_input.setEnabled(False)
        # Use a QDoubleValidator which forbids a user from entering anything other than a number
        weight_input_validator = QDoubleValidator()
        # Specify a range for the weight input to further constrain input (This is not necessary)
        weight_input_validator.setRange(MIN_WEIGHT_INPUT, MAX_WEIGHT_INPUT, decimals=4)
        weight_input.setValidator(weight_input_validator)
        # Use the editingFinished event which is only emitted when the validator emits an Acceptable signal
        weight_input.editingFinished.connect(lambda: validateWeight(weight_input.text()))
        weight_checkbox = QCheckBox("Weighted")
        weight_checkbox.setChecked(True)
        weight_checkbox.clicked.connect(self.scene._graphScene.setWeighted)
        # Add the widgets to the hbox which is then added to the vbox
        weight_hbox.addWidget(weight_checkbox)
        weight_hbox.addWidget(weight_input)
        vbox.addLayout(weight_hbox)
        # Grey out weight input when edge mode is not selected
        toggle_weight_input = lambda: weight_input.setEnabled(self.edge_mode.isChecked() and weight_checkbox.isChecked())
        weight_checkbox.clicked.connect(toggle_weight_input)
        self.edge_mode.toggled.connect(toggle_weight_input)

        self.mode_group = QButtonGroup()
        self.mode_group.addButton(self.select_mode)
        self.mode_group.addButton(self.vertex_mode)
        self.mode_group.addButton(self.edge_mode)
