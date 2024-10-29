from PyQt6.QtGui import QPainter, QDoubleValidator
from PyQt6.QtWidgets import (
    QButtonGroup,
    QGraphicsView,
    QHBoxLayout,
    QRadioButton,
    QVBoxLayout,
    QWidget,
    QLineEdit,
    QPushButton,
)

from ui.scene import Scene
from ui.edge import validateWeight


MAX_WEIGHT_INPUT = 1000
MIN_WEIGHT_INPUT = -1000


class Window(QWidget):
    def __init__(self):
        super().__init__()

        self.scene = Scene(0, 0, 800, 400)

        vbox = QVBoxLayout()

        self.initGraphTypeButtons(vbox)
        self.initStateButtons(vbox)

        view = QGraphicsView(self.scene)
        view.setRenderHint(QPainter.RenderHint.Antialiasing)

        hbox = QHBoxLayout(self)
        hbox.addLayout(vbox)
        hbox.addWidget(view)

        self.setLayout(hbox)
    
    def initGraphTypeButtons(self, vbox):
        vbox_top = QVBoxLayout()

        self.directed_mode = QRadioButton("Directed")
        self.undirected_mode = QRadioButton("Undirected")
        self.confirm_button = QPushButton("Confirm")

        vbox_top.addWidget(self.directed_mode)
        vbox_top.addWidget(self.undirected_mode)
        vbox_top.addWidget(self.confirm_button)

        self.graph_type_group = QButtonGroup()
        self.graph_type_group.addButton(self.directed_mode)
        self.graph_type_group.addButton(self.undirected_mode)
        self.graph_type_group.addButton(self.confirm_button)

        self.directed_mode.setChecked(True)  # Default to directed mode

        self.confirm_button.clicked.connect(self.confirmGraphType)

        vbox.addLayout(vbox_top)
    
    def confirmGraphType(self):
        self.scene.setGraphType("Directed" if self.directed_mode.isChecked() else "Undirected")
        # Grey out the option to select graph type
        self.directed_mode.setEnabled(False)
        self.undirected_mode.setEnabled(False)
        self.confirm_button.setEnabled(False)
        # Make the other buttons selectable
        self.select_mode.setEnabled(True)
        self.vertex_mode.setEnabled(True)
        self.edge_mode.setEnabled(True)

    def initStateButtons(self, vbox):
        self.select_mode = QRadioButton("Select")
        self.select_mode.toggled.connect(self.scene.toggleSelectMode)
        self.select_mode.click()  # select mode is selected on startup
        self.select_mode.setEnabled(False)
        vbox.addWidget(self.select_mode)


        self.vertex_mode = QRadioButton("Vertices")
        self.vertex_mode.toggled.connect(self.scene.toggleVertexMode)
        self.vertex_mode.setEnabled(False)
        vbox.addWidget(self.vertex_mode)

        self.edge_mode = QRadioButton("Edges")
        self.edge_mode.toggled.connect(self.scene.toggleEdgeMode)
        self.edge_mode.setEnabled(False)
        vbox.addWidget(self.edge_mode)

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
        vbox.addWidget(weight_input)
        # Grey out weight input when edge mode is not selected
        toggle_weight_input = lambda: weight_input.setEnabled(self.edge_mode.isChecked())
        self.edge_mode.toggled.connect(toggle_weight_input)

        self.mode_group = QButtonGroup()
        self.mode_group.addButton(self.select_mode)
        self.mode_group.addButton(self.vertex_mode)
        self.mode_group.addButton(self.edge_mode)
