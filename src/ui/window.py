from typing import Optional, Union
import networkx as nx
from PyQt6.QtCore import Qt, QEventLoop, QPoint
from PyQt6.QtGui import QPainter, QDoubleValidator, QIntValidator
from PyQt6.QtWidgets import (
    QButtonGroup,
    QGraphicsView,
    QHBoxLayout,
    QRadioButton,
    QVBoxLayout,
    QWidget,
    QLineEdit,
    QCheckBox,
    QPushButton,
    QSizePolicy,
    QLabel,
    QDialogButtonBox,
)

from ui.scene import Scene
from ui.edge import validateWeight


MAX_WEIGHT_INPUT = 1000
MIN_WEIGHT_INPUT = -1000
MAX_NUM_NODES = 1000
MIN_NUM_NODES = 1


class Window(QWidget):
    def __init__(self, graph: Optional[Union[nx.Graph, nx.DiGraph]]=None):
        super().__init__()

        self.scene = Scene(0, 0, 800, 400, graph)

        vbox = QVBoxLayout()

        self.initGraphGenButton(vbox)
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
    
    def initGraphGenButton(self, vbox):
        self.graph_gen_button = QPushButton("Generate Graph")
        self.graph_gen_button.clicked.connect(self.showGraphGenPopup)
        vbox.addWidget(self.graph_gen_button)

    def showGraphGenPopup(self):
        self.graph_gen_popup = GraphGenPopup(self)
        if self.graph_gen_popup.exec_():
            print("Generated new Graph!")
    
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


class GraphGenPopup(QWidget):
    """Based on https://stackoverflow.com/questions/67029993/pyqt-creating-a-popup-in-the-window"""
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

        from algorithms.random_graph import RandomGraphBuilder
        # Dynamically get public methods from RandomGraphBuilder in case we add more later
        self.graph_methods = [method for method in dir(RandomGraphBuilder) \
                              if callable(getattr(RandomGraphBuilder, method)) \
                              and not method.startswith('_') \
                              and not method == 'build' and not method == 'nodes' \
                              and not method == 'directed' and not method == 'undirected' \
                             ]
        for method in self.graph_methods:
            method_name = ' '.join(word.capitalize() for word in method.split('_'))
            button = QCheckBox(method_name, self)
            button.clicked.connect(lambda _, m=method: self.selectMethod(m))
            layout.addWidget(button)
        layout.addWidget(QLabel('Number of Nodes:'))
        self.num_nodes_input = QLineEdit()
        num_nodes_validator = QIntValidator()
        num_nodes_validator.setRange(MIN_NUM_NODES, MAX_NUM_NODES)
        self.num_nodes_input.setValidator(num_nodes_validator)
        layout.addWidget(self.num_nodes_input)
        self.num_nodes_input.textChanged.connect(self.checkInput)
        self.num_nodes_input.returnPressed.connect(self.accept)

        buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        layout.addWidget(buttonBox)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        self.okButton = buttonBox.button(buttonBox.StandardButton.Ok)
        self.okButton.setEnabled(False)

        parent.installEventFilter(self)
        self.loop = QEventLoop(self)
    
    def checkInput(self):
        text = self.num_nodes_input.text()
        if len(text) == 0 or int(text) == 0:
            self.isNumNodeDefined = False
            self.num_nodes = None
        else:
            self.isNumNodeDefined = True
            self.num_nodes = int(text)

        self.validateInput()

    def selectMethod(self, method):
        if not hasattr(self, 'selected_methods'):
            self.selected_methods = set()
        if method in self.selected_methods:
            self.selected_methods.remove(method)
            if len(self.selected_methods) == 0:
                self.isMethodSelected = False
        else:
            self.selected_methods.add(method)
            self.isMethodSelected = True

        self.validateInput()
    
    def validateInput(self):
        # Check if we haven't defined these before checking them
        if not hasattr(self, 'isMethodSelected'):
            self.isMethodSelected = False
        if not hasattr(self, 'isNumNodeDefined'):
            self.isNumNodeDefined = False

        if self.isMethodSelected and self.isNumNodeDefined:
            self.okButton.setEnabled(True)
        else:
            self.okButton.setEnabled(False)

    def accept(self):
        if self.okButton.isEnabled():
            self.loop.exit(True)

            # Import the newly generated graph to the scene
            graphScene = self.parent().scene._graphScene
            curr_graph = graphScene._graph

            from algorithms.random_graph import RandomGraphBuilder
            new_graph = RandomGraphBuilder(directed=graphScene._isDirected).nodes(self.num_nodes).build()

            combined_graph = nx.disjoint_union(curr_graph, new_graph)
            graphScene._graph = combined_graph
            graphScene.importGraph(combined_graph)

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
