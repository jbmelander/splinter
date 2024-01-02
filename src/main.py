import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget

from data_selection import IOTab
from vis import VisualizationTab

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("splinter")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QTabWidget(self)
        self.setCentralWidget(self.central_widget)
        
        io_tab = IOTab()
        self.central_widget.addTab(io_tab, "IO")

        vis_tab = VisualizationTab()
        self.central_widget.addTab(vis_tab, "Visualization")


def main():
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

