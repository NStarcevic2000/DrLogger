from PyQt5.QtWidgets import QDockWidget, QTabWidget, QWidget
from PyQt5.QtCore import Qt

from util.singleton import singleton

class FOOTER_PAGE:
    FIND_RESULTS = "Find Results"

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
        ]
        for page_name in self.pages:
            self.tab_widget.addTab(None, page_name)

    def get_widget(self, tab_name:str) -> list[QWidget]|QWidget|None:
        return self.tab_widget.widget(self.pages.index(tab_name)) if tab_name in self.pages else None

    def set_widget(self, tab_name:str, widget:QWidget):
        if tab_name in self.pages:
            index = self.pages.index(tab_name)
            self.tab_widget.removeTab(index)
            self.tab_widget.insertTab(index, widget, tab_name)
        else:
            raise ValueError(f"Tab name '{tab_name}' not found in pages.")

    def close_tab(self, index):
        widget = self.tab_widget.widget(index)
        if widget:
            widget.setParent(None)
            widget.deleteLater()
    
    def set_in_focus(self, tab_name:str):
        # If it was previously closed, open it again
        self.show()
        self.raise_()
        self.setFocus()
        if tab_name in self.pages:
            index = self.pages.index(tab_name)
            self.tab_widget.setCurrentIndex(index)