from PyQt5.QtWidgets import QToolBar, QLineEdit, QLabel, QPushButton, QCheckBox
from PyQt5.QtWidgets import QToolButton, QShortcut

from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt

from gui.rendered_logs_table import RenderedLogsTable
from gui.footer_notebook import FOOTER_PAGE, FooterNotebook

class FindToolbar(QToolBar):
    def __init__(self,
                parent,
                searchable_table:RenderedLogsTable):
        self.searchable_table = searchable_table
        super().__init__("Find Toolbar", parent)
        self.label = QLabel("Find:")
        self.label.setMargin(5)
        self.addWidget(self.label)

        self.find_widget = QLineEdit()
        self.find_widget.setPlaceholderText("Enter text to find...")
        self.addWidget(self.find_widget)
        
        self.find_button = QPushButton("Find Next...")
        self.find_button.setToolTip("Find Next (Ctrl+F)")
        self.find_button.clicked.connect(self.find_next)
        self.addWidget(self.find_button)

        self.find_all_button = QPushButton("Find All...")
        self.find_all_button.setToolTip("Find All (?)")
        self.find_all_button.clicked.connect(self.find_all)
        self.addWidget(self.find_all_button)

        self.find_in_collapsed_checkbox = QCheckBox("In collapsed rows")
        self.find_in_collapsed_checkbox.setChecked(False)
        self.find_in_collapsed_checkbox.setToolTip("Search in collapsed rows instead of what is rendered...")
        self.addWidget(self.find_in_collapsed_checkbox)

        self.close_button = QToolButton()
        self.close_button.setText("✕")
        self.close_button.setToolTip("Close")
        self.close_button.setAutoRaise(True)
        self.close_button.setFixedSize(20, 20)
        self.close_button.clicked.connect(self.set_invisible)
        self.addWidget(self.close_button)

        self.setMovable(False)
        self.hide()

        self.search_cache = ("", list())  # (search_text, indexes)
        self.search_all_cache = ("", False, list())  # (search_text, in_collapsed_data, indexes)
        self.searching_index = -1
    
    def toggle_visibility(self):
        if not self.isVisible():
            self.show()
        else:
            self.find_next()
    
    def set_invisible(self):
        self.hide()

    def restart_search(self):
        idx_list = self.searchable_table.get_search_indexes(self.find_widget.text(), show_collapsed=True)
        self.search_cache = (self.find_widget.text(), idx_list)
        self.searching_index = -1
        self.find_next()
    
    def find_next(self, _recursion_guard:int=0):
        if _recursion_guard > 2 or not self.isVisible():
            return
        if self.find_widget.text() and self.find_widget.text() != self.search_cache[0]:
                self.restart_search()
        for row in self.search_cache[1]:
            if row > self.searching_index:
                self.searching_index = row
                # Simulate user click by setting selection and emitting signals
                index = self.searchable_table.model().index(self.searching_index, 0)
                self.searchable_table.setCurrentIndex(index)
                self.searchable_table.selectionModel().select(index, self.searchable_table.selectionModel().Select)
                self.searchable_table.scrollTo(
                    self.searchable_table.model().index(self.searching_index, 0),
                    self.searchable_table.PositionAtCenter
                )
                return
        self.searching_index = -1
        self.find_next(_recursion_guard + 1)
    
    def find_all(self):
        if self.find_widget.text() and self.find_widget.text() != self.search_all_cache[0] or \
           self.find_in_collapsed_checkbox.isChecked() != self.search_all_cache[1]:
            show_collapsed = self.find_in_collapsed_checkbox.isChecked()
            # If we already cached search indexes for "Find Next", reuse them
            # Since "Find Next" always searches in collapsed data, only reuse if searching in collapsed data
            if show_collapsed and self.find_widget.text() == self.search_cache[0]:
                idx_list = self.search_cache[1]
            else:
                # Iloc indexes
                idx_list = self.searchable_table.get_search_indexes(self.find_widget.text(), show_collapsed=show_collapsed)
                # Actual indexes
                idx_list = [self.searchable_table.model()._visible_data.index[i] for i in idx_list]
            self.search_all_cache = (self.find_widget.text(), show_collapsed, idx_list)
        # Show results in the footer table
        render_logs_table = FooterNotebook().get_widget(FOOTER_PAGE.FIND_RESULTS)
        if isinstance(render_logs_table, RenderedLogsTable):
            render_logs_table.refresh(
                specific_rows=self.search_all_cache[2],
                show_collapsed=self.search_all_cache[1]
            )
        else:
            render_logs_table = RenderedLogsTable()
            FooterNotebook().set_widget(FOOTER_PAGE.FIND_RESULTS, render_logs_table)
            render_logs_table.refresh(
                specific_rows=self.search_all_cache[2],
                show_collapsed=self.search_all_cache[1]
            )
