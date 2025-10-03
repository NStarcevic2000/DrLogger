from PyQt5.QtWidgets import QToolBar, QMenu, QAction, QToolButton

class MainToolbar(QToolBar):
    def __generate_submenu(self, data: dict, parent):
        items = []
        for key, value in data.items():
            if isinstance(value, dict):
                submenu = QMenu(key, parent)
                subitems = self.__generate_submenu(value, parent)
                for item in subitems:
                    if isinstance(item, QMenu):
                        submenu.addMenu(item)
                    else:
                        submenu.addAction(item)
                items.append(submenu)
            elif callable(value):
                action = QAction(key, parent)
                action.triggered.connect(value)
                items.append(action)
        return items

    def __init__(self, data:dict, parent):
        super().__init__("Main Toolbar", parent)
        for item in self.__generate_submenu(data, parent):
            if isinstance(item, QMenu):
                menu_button = QToolButton(self)
                menu_button.setText(item.title())
                menu_button.setMenu(item)
                menu_button.setPopupMode(QToolButton.InstantPopup)
                # Remove the arrow indicator for the dropdown
                menu_button.setStyleSheet("QToolButton::menu-indicator { image: none; }")
                self.addWidget(menu_button)
            else:
                self.addAction(item)