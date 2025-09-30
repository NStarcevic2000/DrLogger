from PyQt5.QtWidgets import QVBoxLayout, QLabel, QWidget, QHBoxLayout, QFrame, QToolButton
from PyQt5.QtCore import Qt

from pandas import DataFrame

from gui.common.metadata_elements import MetadataType
from util.singleton import singleton
from logs_managing.logs_manager import LogsManager

from gui.footer_notebook import FooterNotebook, FOOTER_PAGE
from PyQt5.QtWidgets import QScrollArea, QVBoxLayout, QWidget



class MetadataWidget(QWidget):
    # Metadata Header
    class MetadataHeader(QWidget):
        def __init__(self, category: str):
            super().__init__()
            self.button = QToolButton()
            self.button.setArrowType(Qt.RightArrow)
            self.button.setFocusPolicy(Qt.NoFocus)
            self.button.setCursor(Qt.PointingHandCursor)
            self.button.clicked.connect(self._on_header_clicked)
            self.label = QLabel(f"<b>{category}</b>")
            layout = QHBoxLayout()
            layout.addWidget(self.button)
            layout.addWidget(self.label)
            layout.addStretch(1)
            self.setLayout(layout)
            self.setCursor(Qt.PointingHandCursor)
            self.setObjectName("MetadataWidget_MetadataHeader")
            self.setStyleSheet("""
            #MetadataWidget_MetadataHeader {
                margin: 0px;
                padding: 5px;
                border-radius: 5px;
                background-color: #f0f0f0;
            }
            #MetadataWidget_MetadataHeader:hover {
                background-color: #e0e0e0;
            }
            QToolButton {
                border: none;
                width: 15px;
                height: 15px;
                background-color: transparent;
            }
            QLabel {
                background-color: transparent;
            }
            """)
            self._frame = None
            self._expanded = False
    
        def connect_collapsable(self, frame: QFrame) -> QWidget:
            self._frame = frame
            self._frame.setVisible(self._expanded)
            return self

        def mousePressEvent(self, event):
            self._on_header_clicked()
            super().mousePressEvent(event)

        def _on_header_clicked(self):
            if self._frame is not None:
                self._expanded = not self._expanded
                self._update_arrow_and_frame()

        def paintEvent(self, event):
            super().paintEvent(event)

        def _update_arrow_and_frame(self):
            self.button.setArrowType(Qt.DownArrow if self._expanded else Qt.RightArrow)
            if self._frame is not None:
                self._frame.setVisible(self._expanded)
    
    # Metadata Frame
    class MetadataFrame(QFrame):
        def __init__(self, details:dict):
            super().__init__()
            self.setFrameShape(QFrame.StyledPanel)
            self.setStyleSheet("""
                QFrame#MetadataWidget_MetadataFrame {
                    border: 1px solid #cccccc;
                    border-radius: 6px;
                    background-color: #fafafa;
                    margin-top: 2px;
                    margin-bottom: 2px;
                }
            """)
            self.setObjectName("MetadataWidget_MetadataFrame")
            layout = QVBoxLayout()
            for key, value in details.items():
                if isinstance(value, MetadataType):
                    label = QLabel(f"<b>{key}:</b>")
                    label.setTextInteractionFlags(Qt.TextSelectableByMouse)
                    layout.addWidget(label)
                    layout.addWidget(value.get_widget())
                else:
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
                header = self.MetadataHeader(category)
                header.connect_collapsable(frame)
                layout.addWidget(header)
                layout.addWidget(frame)
        layout.addStretch(1)
        self.setLayout(layout)
        self.repaint()



@singleton
class MetadataContent():
    ''' Manages the generation and display of metadata for log entries. '''
    # Define column names to keep parity between metadata Dataframe and generated QWidgets
    __WIDGET = "WIDGET"
    __METADATA = "METADATA"

    def __init__(self):
        self.metadata = DataFrame()
        self.prepare_for_generating()

    def prepare_for_generating(self):
        self.metadata = DataFrame(LogsManager().get_metadata(), columns=[self.__METADATA])
        self.metadata.insert(0, self.__WIDGET, None)

    def show_in_footer(self, index:int):
        self.generate_for_line(index, show_in_footer=True)
    
    def generate_for_line(self, index:int, show_in_footer:bool=False):
        ''' Force generate metadata for a specific line index. 
            In case of running in a background, it will request this one to be done immediatly.
        '''
        index = self.metadata.index[index]
        widget = self.metadata.at[index, self.__WIDGET]
        if widget is not None:
            if show_in_footer:
                FooterNotebook().set_widget(FOOTER_PAGE.METADATA, widget)
        else:
            # Wrap MetadataWidget in a scrollable area
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            content_widget = MetadataWidget(self.metadata.at[index, self.__METADATA])
            scroll.setWidget(content_widget)
            scroll.setFrameShape(QScrollArea.NoFrame)
            self.metadata.at[index, self.__WIDGET] = scroll
            if show_in_footer:
                FooterNotebook().set_widget(FOOTER_PAGE.METADATA, scroll)
    
    def generate_for_all(self):
        ''' Generate Metadata for all lines. '''
        self.prepare_for_generating()
        for i in range(len(self.metadata)):
            self.generate_for_line(i)