# main.py
import sys
from PyQt5.QtWidgets import QApplication

from configStoreImpl import masterConfigStore

from processor.processPipeline import ProcessPipeline

from gui.mainWindow import DrLogMainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    processPipeline = ProcessPipeline(masterConfigStore)

    viewer = DrLogMainWindow(masterConfigStore, processPipeline)
    viewer.show()

    sys.exit(app.exec_())