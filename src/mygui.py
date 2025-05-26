from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QFileDialog, QVBoxLayout, QWidget, QHBoxLayout, QTextEdit, QComboBox, QTabWidget
from PyQt6.QtCore    import Qt, QUrl, QThread, pyqtSignal
from PyQt6.QtGui     import QDragEnterEvent, QMouseEvent

from .gui.translate_gui import TranslateWidget
from .gui.tts import  TTSWidget

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("歐陽神器")
        layout = QVBoxLayout()

        self.tabs = QTabWidget()
        self.tabs.addTab(TranslateWidget(), "簡易翻譯器")
        self.tabs.addTab(TTSWidget(), "語音轉文字")

        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def first_tab_ui(self):
        tab = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("這是第一個頁面"))
        tab.setLayout(layout)
        return tab

