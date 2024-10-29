from PyQt6.QtGui import QPainter, QDoubleValidator
from PyQt6.QtWidgets import (
    QButtonGroup,
    QGraphicsView,
    QHBoxLayout,
    QRadioButton,
    QVBoxLayout,
    QWidget,
    QLineEdit,
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

        self.initStateButtons(vbox)

        view = QGraphicsView(self.scene)
        view.setRenderHint(QPainter.RenderHint.Antialiasing)

        hbox = QHBoxLayout(self)
        hbox.addLayout(vbox)
        hbox.addWidget(view)

        self.setLayout(hbox)

    def initStateButtons(self, vbox):
        select_mode = QRadioButton("Select")
        select_mode.toggled.connect(self.scene.toggleSelectMode)
        vbox.addWidget(select_mode)

        select_mode.click()  # select mode is selected on startup

        vertex_mode = QRadioButton("Vertices")
        vertex_mode.toggled.connect(self.scene.toggleVertexMode)
        vbox.addWidget(vertex_mode)

        edge_mode = QRadioButton("Edges")
        edge_mode.toggled.connect(self.scene.toggleEdgeMode)
        vbox.addWidget(edge_mode)

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
        toggle_weight_input = lambda: weight_input.setEnabled(edge_mode.isChecked())
        edge_mode.toggled.connect(toggle_weight_input)

        mode_group = QButtonGroup()
        mode_group.addButton(select_mode)
        mode_group.addButton(vertex_mode)
        mode_group.addButton(edge_mode)
