import threading
from PyQt5.QtWidgets import QStatusBar, QLabel
from PyQt5.QtWidgets import QStatusBar, QLabel, QProgressBar
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication

class StatusManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(StatusManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.status_bar = StatusBar()
    
    def get_status_bar(self):
        return self.status_bar

class StatusBar(QStatusBar):
    def __init__(self):
        super().__init__()
        self.setSizeGripEnabled(False)
        self.setVisible(True)
        
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setVisible(True)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(0)
        self.progress_bar.setFixedWidth(200)
        self.progress_bar.setFixedHeight(14)
        self.progress_bar.setContentsMargins(0, 0, 0, 0)

        self.label = QLabel(self)
        self.label.setMinimumWidth(100)
        self.label.setContentsMargins(2, 0, 0, 0)

        self.contentPadding = 5

        # Add progress bar first, then label to the right
        self.addPermanentWidget(self.progress_bar)
        self.addPermanentWidget(self.label)
        self.stop_progress()

    def set_status(self, text: str):
        self.label.setText(text)

    def set_enabled(self, enabled: bool):
        self.setEnabled(enabled)

    def start_progress(self):
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(0)

    def stop_progress(self):
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.label.setText("Ready")

    def call_in_background(self, background_cmd: callable, on_done: callable = None):
        """Run worker_method in a separate thread, then call on_done in the main thread when finished."""
        def worker():
            background_cmd()
            self.stop_progress()
            self.set_status("Ready")
            if on_done:
                QTimer.singleShot(0, on_done)

        self.start_progress()
        self.set_status("Processing...")
        thread = threading.Thread(target=worker)
        thread.start()
    
    def call(self, cmd: callable):
        """Run cmd in the main thread. (For long GUI processes)"""
        self.set_status("Processing...")
        self.start_progress()
        QApplication.processEvents()
        cmd()
        self.set_status("Ready")
        self.stop_progress()