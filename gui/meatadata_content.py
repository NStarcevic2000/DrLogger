from PyQt5.QtWidgets import QVBoxLayout, QLabel, QWidget, QHBoxLayout, QFrame, QToolButton
from PyQt5.QtCore import Qt

from pandas import DataFrame

from util.singleton import singleton
from util.logs_manager import LogsManager

from gui.footer_notebook import FooterNotebook, FOOTER_PAGE



class MetadataWidget(QWidget):
    # Metadata Header
    class MetadataHeader(QWidget):
        def __init__(self, category:str):
            super().__init__()
            self.button = QToolButton()
            self.button.setArrowType(Qt.RightArrow)
            label = QLabel(f"<b>{category}</b>")
            layout = QHBoxLayout()
            layout.addWidget(self.button)
            layout.addWidget(label)
            layout.addStretch(1)
            self.setLayout(layout)
            self.setStyleSheet("""
                margin: 0px;
                padding: 5px;
                border-radius: 5px;
                background-color: #f0f0f0;
                QToolButton {
                    border: none;
                    width: 15px;
                    height: 15px;
                    background-color: transparent;
                }
                QToolButton::hover { background-color: lightgray; }
                QLabel {
                    background-color: transparent;
                }
            """)
        def connect_collapsable(self, frame:QFrame) -> QWidget:
            self.button.setCheckable(True)
            self.button.clicked.connect(
                lambda checked, b=self.button, f=frame:
                    (b.setArrowType(Qt.DownArrow if checked else Qt.RightArrow), f.setVisible(checked))
            )
            return self
    # Metadata Frame
    class MetadataFrame(QFrame):
        def __init__(self, details:dict):
            super().__init__()
            self.setFrameShape(QFrame.StyledPanel)
            layout = QVBoxLayout()
            for key, value in details.items():
                label = QLabel(f"<b>{key}:</b> {value}")
                label.setTextInteractionFlags(Qt.TextSelectableByMouse)
                layout.addWidget(label)
            layout.addStretch(1)
            self.setLayout(layout)
            self.setVisible(False)
    
    # Container for both
    def __init__(self, metadata:dict):
        super().__init__()
        self.metadata = None
        self.update(metadata)
    
    def update(self, metadata:dict):
        if self.metadata == metadata:
            return
        self.metadata = metadata
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(2)
        for category, details in metadata.items():
            if isinstance(details, dict):
                frame = self.MetadataFrame(details)
                header = self.MetadataHeader(category).connect_collapsable(frame)
                layout.addWidget(header)
                layout.addWidget(frame)
        layout.addStretch(1)
        self.setLayout(layout)
        self.repaint()



@singleton
class MetadataContent():
    ''' Manages the generation and display of metadata for log entries. '''
    # Define column names to keep parity between metadata Dataframe and generated QWidgets
    __IS_RUNNING = "IS RUNNING"
    __METADATA = "METADATA"

    def __init__(self):
        self._current_data = DataFrame()
        self.prepare_for_generating()

    def prepare_for_generating(self):
        _, self._current_data = LogsManager().get_data(show_collapsed=True)
        self._current_data.insert(0, self.__IS_RUNNING, False)
        self._current_data.insert(1, self.__METADATA, None)

    def show_in_footer(self, index:int):
        self.generate_for_line(index, show_in_footer=True)
    
    def generate_for_line(self, index:int, show_in_footer:bool=False):
        ''' Force generate metadata for a specific line index. 
            In case of running in a background, it will request this one to be done immediatly.
        '''
        if self._current_data.at[index, self.__METADATA] is not None:
            if show_in_footer:
                FooterNotebook().set_widget(FOOTER_PAGE.METADATA, self._current_data.at[index, self.__METADATA])
        if not self._current_data.at[index, self.__IS_RUNNING]:
            # Mark as running
            self._current_data.at[index, self.__IS_RUNNING] = True
            # try:
            gen_dict = {}
            print("Have metadata:", self._current_data.head(5))
            for col in self._current_data.columns[2:]: # Skip IS_RUNNING and METADATA columns
                if isinstance(self._current_data.at[index, col], dict):
                    # Deep merge dictionaries to handle nested structures
                    def deep_update(d, u):
                        for k, v in u.items():
                            if isinstance(v, dict) and isinstance(d.get(k), dict):
                                deep_update(d[k], v)
                            else:
                                d[k] = v
                    deep_update(gen_dict, self._current_data.at[index, col])
                    print("After merge:", gen_dict)
                else:
                    print(f"Skipping non-dict metadata for column {col}: {self._current_data.at[index, col]}")
            generate_widget = MetadataWidget(gen_dict)
            self._current_data.at[index, self.__METADATA] = generate_widget
            if show_in_footer:
                FooterNotebook().set_widget(FOOTER_PAGE.METADATA, generate_widget)
            # except Exception as e:
            #     print(f"Error generating metadata for line {index}: {e}")
            #finally:
                # Mark as not running
            self._current_data.at[index, self.__IS_RUNNING] = False
            

    
    def generate_for_all(self):
        ''' Generate Metadata for all lines. '''
        self.prepare_for_generating()
        for i in range(len(self._current_data)):
            self.generate_for_line(i)
