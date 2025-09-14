from PyQt5.QtWidgets import QVBoxLayout, QLabel, QWidget, QHBoxLayout, QFrame, QToolButton

from pandas import DataFrame

from util.singleton import singleton
from util.logs_manager import LogsManager

from gui.footer_notebook import FooterNotebook

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
            return self._current_data.at[index, self.__METADATA]
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
            generate_widget = self.generate_widget(gen_dict)
            self._current_data.at[index, self.__METADATA] = generate_widget
            if show_in_footer:
                FooterNotebook().set_widget("Metadata", generate_widget)
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
    
    def generate_widget(self, metadata:dict) -> QWidget:
        ''' Generate a QWidget to display the metadata dictionary. '''
        widget = QWidget()
        vbox = QVBoxLayout(widget)
        # Parse by category
        for category, details in metadata.items():
            print(f"Generating category: {category} with details: {details}")
            # Define the Widget content
            category_header_container = QHBoxLayout()
            
            category_header_collapsable_button = QToolButton()
            category_header_collapsable_button.setText("▶")
            category_header_collapsable_button.setCheckable(True)
            category_header_container.addWidget(category_header_collapsable_button)

            category_header_label = QLabel(f"<b>{category}</b>")
            category_header_container.addWidget(category_header_label)

            category_details_frame = QFrame()
            category_details_frame.setFrameShape(QFrame.StyledPanel)
            category_details_frame.setVisible(False)

            # Toggle visibility on button click
            def toggle_details_visibility(checked, button=category_header_collapsable_button, frame=category_details_frame):
                if checked:
                    button.setText("▼")
                    frame.setVisible(True)
                else:
                    button.setText("▶")
                    frame.setVisible(False)
            category_header_collapsable_button.toggled.connect(toggle_details_visibility)

            # Present each detail in the category
            category_details_layout = QVBoxLayout()
            for key, value in details.items():
                print("Generating detail:", key, value)
                detail_label = QLabel(f"{key}: {value}")
                category_details_layout.addWidget(detail_label)
            category_details_frame.setLayout(category_details_layout)
            vbox.addLayout(category_header_container)
            vbox.addWidget(category_details_frame)
        vbox.addStretch(1)
        widget.setLayout(vbox)
        return widget
