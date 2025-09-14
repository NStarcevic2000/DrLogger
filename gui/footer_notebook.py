from PyQt5.QtWidgets import QDockWidget, QTabWidget, QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt

from util.singleton import singleton

class FOOTER_PAGE:
    FIND_RESULTS = "Find Results"
    METADATA = "Metadata"

@singleton
class FooterNotebook(QDockWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAllowedAreas(Qt.BottomDockWidgetArea)

        self.tab_widget = QTabWidget()
        self.setWidget(self.tab_widget)
        # self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.pages = [
            FOOTER_PAGE.FIND_RESULTS,
            FOOTER_PAGE.METADATA
        ]
        for page_name in self.pages:
            self.tab_widget.addTab(self.get_empty_widget(), page_name)

    def get_widget(self, tab_name:str) -> list[QWidget]|QWidget|None:
        return self.tab_widget.widget(self.pages.index(tab_name)) if tab_name in self.pages else None

    def set_widget(self, tab_name:str, widget:QWidget):
        if tab_name in self.pages:
            print("Replacing existing tab:", tab_name)
            index = self.pages.index(tab_name)
            # Replace the existing widget in the tab
            self.tab_widget.removeTab(index)
            self.tab_widget.insertTab(index, widget, tab_name)
            self.tab_widget.setCurrentIndex(index)
        else:
            print("Adding new tab:", tab_name)
            self.pages.append(tab_name)
            self.tab_widget.addTab(widget, tab_name)
            self.tab_widget.setCurrentIndex(self.tab_widget.count() - 1)
        self.set_in_focus(tab_name)

    def close_tab(self, index):
        widget = self.tab_widget.widget(index)
        if widget:
            widget.setParent(None)
            widget.deleteLater()
    
    def set_in_focus(self, tab_name:str):
        print("Setting footer notebook in focus:", tab_name)
        self.show()
        self.raise_()
        self.setFocus(Qt.ActiveWindowFocusReason)
        if tab_name in self.pages:
            index = self.pages.index(tab_name)
            self.tab_widget.setCurrentIndex(index)
    
    def get_empty_widget(self) -> QWidget:
        # Just show in a centered text that there is no content
        empty_widget = QWidget()
        empty_widget.setLayout(QVBoxLayout())
        label = QLabel("No content available")
        label.setAlignment(Qt.AlignCenter)
        empty_widget.layout().addWidget(label)
        return empty_widget