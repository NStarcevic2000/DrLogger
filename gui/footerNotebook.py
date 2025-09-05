from PyQt5.QtWidgets import QDockWidget, QTabWidget
from PyQt5.QtCore import Qt

class FooterNotebook(QDockWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAllowedAreas(Qt.BottomDockWidgetArea)

        self.tab_widget = QTabWidget()
        self.setWidget(self.tab_widget)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)

        self.tab_widget.addTab(QTabWidget(), "Welcome")

    def add_tab(self, widget, title):
        self.tab_widget.addTab(widget, title)

    def close_tab(self, index):
        self.tab_widget.removeTab(index)