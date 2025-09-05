from PyQt5.QtWidgets import QToolBar, QLineEdit, QLabel, QPushButton
from PyQt5.QtWidgets import QToolButton

class FindToolbar(QToolBar):
    def __init__(self,
                parent,
                main_table=None):
        super().__init__("Find Toolbar", parent)
        self.label = QLabel("Find:")
        self.label.setMargin(5)
        self.addWidget(self.label)

        self.find_widget = QLineEdit()
        self.find_widget.setPlaceholderText("Enter text to find...")
        self.addWidget(self.find_widget)

        self.find_button = QPushButton("Find Next...")
        self.addWidget(self.find_button)

        self.find_all_button = QPushButton("Find All...")
        self.addWidget(self.find_all_button)

        self.close_button = QToolButton()
        self.close_button.setText("✕")
        self.close_button.setToolTip("Close")
        self.close_button.setAutoRaise(True)
        self.close_button.setFixedSize(20, 20)
        self.close_button.clicked.connect(self.hide)
        self.addWidget(self.close_button)

        self.setMovable(False)
        self.hide()
    
    def toggle_visibility(self):
        if not self.isVisible():
            self.show()
        else:
            print("Call find command")