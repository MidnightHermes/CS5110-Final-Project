import networkx as nx
from PyQt6.QtCore import Qt, QEventLoop, QPersistentModelIndex, QPoint, QStringListModel
from PyQt6.QtGui import QIntValidator
from PyQt6.QtWidgets import (
    QDoubleSpinBox,
    QGroupBox,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QLineEdit,
    QListView,
    QCheckBox,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QLabel,
    QDialogButtonBox,
)

MAX_NUM_NODES = 1000
MIN_NUM_NODES = 1

class BuilderOptionListModel(QStringListModel):
    def __init__(self, *args, **kwargs):
        super(QStringListModel, self).__init__(*args, **kwargs)

    def flags(self, *args):
        return (Qt.ItemFlag.ItemIsSelectable
                | Qt.ItemFlag.ItemIsDragEnabled
                | Qt.ItemFlag.ItemIsDropEnabled
                | Qt.ItemFlag.ItemIsEnabled
                | Qt.ItemFlag.ItemNeverHasChildren)
    
class BuildOptionListView(QListView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._canDelete = False
        self._onCopy = None
        self._map = {}

    def allowDeletion(self, on):
        self._canDelete = on

    def mouseDoubleClickEvent(self, event):
        if self._canDelete and event.button() == Qt.MouseButton.LeftButton:
            index = self.currentIndex()

            persistent = QPersistentModelIndex(index)
            del self._map[persistent]

            index.row()
            self.model().removeRow(index.row())
        else:
            super().mouseDoubleClickEvent(event)

    def getLastIndex(self):
        return self.model().index(self.model().rowCount() - 1, 0)
        
    def onCopy(self, f):
        self._onCopy = f

    def values(self):
        mapRows = {p.row(): v for (p, v) in self._map.items()}

        return [mapRows[n] for n in sorted(mapRows.keys())]

    def dropEvent(self, event):
        super().dropEvent(event)

        if event.dropAction() == Qt.DropAction.CopyAction:
            dropPos = event.position().toPoint()

            errDown = QPoint(dropPos.x(), dropPos.y() + 10)

            indexOfDrop = self.indexAt(dropPos)
            indexErrDown = self.indexAt(errDown)

            if indexOfDrop != indexErrDown:
                indexOfDrop = indexErrDown

            last = self.getLastIndex()

            correctIndex = indexOfDrop if indexOfDrop.row() > -1 else last
            name = self.model().data(correctIndex)

            if self._onCopy is not None:
                val = self._onCopy(name)

                persistent = QPersistentModelIndex(last)
                
                self._map[persistent] = val

class GraphGenPopup(QWidget):
    """
    Based on https://stackoverflow.com/questions/67029993/pyqt-creating-a-popup-in-the-window
    and https://www.youtube.com/watch?v=TlLxyuQKbv4

    To extend, go to the methods property
    """
    def __init__(self, parent):
        super().__init__(parent)

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

        self.container = QWidget(autoFillBackground=True, objectName='container')

        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.addWidget(self.container, alignment=Qt.AlignmentFlag.AlignCenter)
        self.container.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        self.container.setFixedHeight(parent.height())

        buttonSize = self.fontMetrics().height()
        self.closeButton = QPushButton('x', self.container, objectName='close')
        self.closeButton.setFixedSize(buttonSize, buttonSize)
        self.closeButton.clicked.connect(self.reject)

        vLayout = QVBoxLayout(self.container)
        vLayout.setContentsMargins(buttonSize * 2, buttonSize, buttonSize * 2, buttonSize)

        title = QLabel('Select a graph generation method', objectName='title', alignment=Qt.AlignmentFlag.AlignCenter)
        vLayout.addWidget(title)

        self.hLayout = QHBoxLayout()
        vLayout.addLayout(self.hLayout)

        self.buildLists()

        vLayout.addWidget(QLabel('Number of Nodes:'))
        self.num_nodes_input = QLineEdit()
        num_nodes_validator = QIntValidator()
        num_nodes_validator.setRange(MIN_NUM_NODES, MAX_NUM_NODES)
        self.num_nodes_input.setValidator(num_nodes_validator)
        self.num_nodes_input.textChanged.connect(self.checkInput)
        vLayout.addWidget(self.num_nodes_input)
        self.num_nodes_input.textChanged.connect(self.checkInput)
        self.num_nodes_input.returnPressed.connect(self.accept)

        buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        vLayout.addWidget(buttonBox)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        self.okButton = buttonBox.button(buttonBox.StandardButton.Ok)
        self.okButton.setEnabled(False)

        # parent.installEventFilter(self)
        self.loop = QEventLoop(self)

    @property
    def methods(self):
        from algorithms.random_graph import RandomGraphBuilder

        

        clique = {RandomGraphBuilder.clique:
                    {'name': 'Clique',
                     'args': [('size', BuilderOptionPopup.BuilderArgument.INT),
                              ('add_new_nodes', BuilderOptionPopup.BuilderArgument.BOOL)]}}

        random_edges = {RandomGraphBuilder.random_edges:
                            {'name': 'Random Edges',
                             'args': [('p', BuilderOptionPopup.BuilderArgument.REAL),
                                      ('backwards_edges', BuilderOptionPopup.BuilderArgument.BOOL)]}}

        complete = {RandomGraphBuilder.complete:
                        {'name': 'Complete',
                         'args': []}}
        
        connected = {RandomGraphBuilder.connected:
                        {'name': 'Connected',
                         'args': []}}
        
        strongly_connected = {RandomGraphBuilder.strongly_connected:
                                {'name': 'Strongly Connected',
                                 'args': [('backwards_edges', BuilderOptionPopup.BuilderArgument.BOOL)]}}
    
        spanning_tree = {RandomGraphBuilder.spanning_tree:
                            {'name': 'Spanning Tree',
                             'args': []}}
        
        weighted = {RandomGraphBuilder.weighted:
                        {'name': 'Weighted',
                         'args': [('weight_range', BuilderOptionPopup.BuilderArgument.RANGE)]}}
        
        cycle = {RandomGraphBuilder.cycle:
                    {'name': 'Cycle',
                     'args': [('length', BuilderOptionPopup.BuilderArgument.INT),
                              ('negative_weight', BuilderOptionPopup.BuilderArgument.BOOL)]}}
        
        # To add more. make a dict with the method as the key, then the value is another dict with
        # a name pair and args mapping. args maps to a list of pairs containing the exact name of the
        # function argument with the BuilderArgument type. Then add the new item to the union below.

        return (clique
                | random_edges
                | complete
                | connected
                | strongly_connected
                | spanning_tree
                | weighted
                | cycle)
    
    def buildLists(self):
        self.optionList = QListView(self)
        self.optionList.setDragEnabled(True)
        self.optionList.setAcceptDrops(False)
        self.optionList.setDropIndicatorShown(True)
        self.optionList.setDefaultDropAction(Qt.DropAction.CopyAction)
        self.hLayout.addWidget(self.optionList)

        self.buildList = BuildOptionListView(self)
        self.buildList.setDragEnabled(True)
        self.buildList.setAcceptDrops(True)
        self.buildList.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.buildList.setDropIndicatorShown(True)
        self.buildList.allowDeletion(True)

        self.hLayout.addWidget(self.buildList)

        methods = self.methods
        name_map = {i['name']: (m, i) for (m, i) in methods.items()}

        def popupCallback(name):
            method, info = name_map[name]

            pop = BuilderOptionPopup(self, info)
            return (method, pop.exec_())

        self.buildList.onCopy(popupCallback)
        optionModel = BuilderOptionListModel(name_map.keys())
        self.optionList.setModel(optionModel)
        self.buildList.setModel(BuilderOptionListModel())

        self.optionList.setStyleSheet('''
            QListView { font-size: 10pt; font-weight: bold; }
            QListView::item { background-color: #E0E0E0; padding: 10%;
                             border: 1px solid #000000; }
            QListView::item::hover { background-color: #C0C0C0 }
        ''')

        self.buildList.setStyleSheet('''
            QListView { font-size: 10pt; font-weight: bold; }
            QListView::item { background-color: #2ECC71; padding: 10%;
                             border: 1px solid #27AE60; }
            QListView::item::hover { background-color: #27AE60 }
        ''')        
    
    def checkInput(self):
        text = self.num_nodes_input.text()
        if len(text) == 0 or int(text) == 0:
            self.isNumNodeDefined = False
            self.num_nodes = None
            self.okButton.setEnabled(False)
        else:
            self.okButton.setEnabled(True)
            self.isNumNodeDefined = True
            self.num_nodes = int(text)

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

    def accept(self):
        if self.okButton.isEnabled():
            self.loop.exit(True)

            # Import the newly generated graph to the scene
            graphScene = self.parent().scene._graphScene
            curr_graph = graphScene._graph

            steps = self.buildList.values()
            new_graph = nx.DiGraph() if graphScene._isDirected else nx.Graph()
            new_graph.add_nodes_from(range(self.num_nodes))
            for f, args in steps:
                new_graph = f(new_graph, **args)

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
    
import enum

class BuilderOptionPopup(QWidget):
    # Extend this if there is a new kind of argument needed for the builder methods.
    # If extended, must add a new case to the generate method
    class BuilderArgument(enum.Enum):
        INT = enum.auto()
        BOOL = enum.auto()
        RANGE = enum.auto()
        REAL = enum.auto()

    def __init__(self, parent, fInfo):
        super().__init__(parent)

        self.setStyleSheet('''
            QWidget#container {
                border: 2px solid darkGray;
                border-radius: 4px;
                padding: 10%;
            }
            
            QLabel#title {
                font-size: 20pt;
            }
                           
            QGroupBox {
                color: white;
            }
        ''')

        self._fInfo = fInfo

        name = fInfo['name']

        self.container = QWidget(autoFillBackground=True, objectName='container')

        mainLayout = QVBoxLayout(self)
        mainLayout.addWidget(self.container, alignment=Qt.AlignmentFlag.AlignCenter)
        self.container.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)

        buttonSize = self.fontMetrics().height()

        vLayout = QVBoxLayout(self.container)
        vLayout.setContentsMargins(0, 0, buttonSize, buttonSize)

        title = QLabel(name, objectName='title', alignment=Qt.AlignmentFlag.AlignCenter)
        vLayout.addWidget(title)

        vLayout.addLayout(self.generate(fInfo['args']))

        buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        vLayout.addWidget(buttonBox)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        self.okButton = buttonBox.button(buttonBox.StandardButton.Ok)

        self.loop = QEventLoop(self)

    def generate(self, map):
        layout = QVBoxLayout()

        self._grabbers = []

        for name, t in map:
            parent = QGroupBox(name)
            littleLayout = QVBoxLayout()
            
            # The name has to be copied under a different variable name,
            # and similar goes with the widget in order for the lambdas to work correctly.
            match t:
                case self.BuilderArgument.INT:
                    spin = QSpinBox()
                    namespin = name[:]
                    self._grabbers.append(lambda: (namespin, spin.value()))
                    widg = spin
                case self.BuilderArgument.REAL:
                    spind = QDoubleSpinBox()
                    namespind = name[:]
                    self._grabbers.append(lambda: (namespind, spind.value()))
                    widg = spind
                case self.BuilderArgument.BOOL:
                    check = QCheckBox()
                    namecheck = name[:]
                    self._grabbers.append(lambda: (namecheck, check.isChecked()))
                    widg = check
                case self.BuilderArgument.RANGE:
                    widg = QGroupBox()
                    hLayout = QHBoxLayout()

                    low = QSpinBox()
                    low.setObjectName(name + 'low')
                    hLayout.addWidget(low)

                    high = QSpinBox()
                    high.setObjectName(name + 'high')
                    hLayout.addWidget(high)

                    namer = name[:]
                    def grab():
                        lowVal = low.value()
                        highVal = high.value()
                        return (namer, range(lowVal, highVal))
                    
                    self._grabbers.append(grab)

                    widg.setLayout(hLayout)
                case _:
                    raise ValueError("BuilderArgument type not supported")

            widg.setObjectName(name)
            littleLayout.addWidget(widg)

            parent.setLayout(littleLayout)
            layout.addWidget(parent)

        return layout

    def accept(self):
        self.loop.exit(True)

    def reject(self):
        # TODO: delete item on reject
        self.loop.exit(False)

    def showEvent(self, event):
        self.setGeometry(self.parent().rect())

    def eventFilter(self, source, event):
        if event.type() == event.Type.Resize:
            self.setGeometry(source.rect())
        return super().eventFilter(source, event)

    def exec_(self):
        if len(self._fInfo['args']) == 0:
            return []

        self.show()
        self.raise_()
        res = self.loop.exec()
        self.hide()

        mappings = [f() for f in self._grabbers]
        return {m: a for (m, a) in mappings} if res else None
