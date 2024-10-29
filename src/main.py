import sys
from PyQt6.QtWidgets import QApplication
import networkx as nx

from ui.window import Window
from algorithms.random_graph import RandomGraph


def main():
    app = QApplication(sys.argv)

    # w = Window(RandomGraph(directed=True).graph)
    w = Window()
    w.show()

    app.exec()


if __name__ == '__main__':
    main()
