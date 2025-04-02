import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QFileDialog, QVBoxLayout, QWidget
from PyQt6.QtCore   import Qt
from PyQt6.QtGui    import QDragEnterEvent

from .translator import MyTranslator

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("  SRT簡體轉繁體，歐陽出品")
        self.setGeometry(100, 100, 600, 400)

        # 设置中心小部件和布局
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout : QVBoxLayout= QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # 标签用于显示拖放信息
        self.label = QLabel("把任何文字文件拖到这里\n我都會幫你轉換成繁體")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.label)

        # 启用拖放
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event : QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event : QDragEnterEvent):
        # 获取拖放的文件路径
        file_path = event.mimeData().urls()[0].toLocalFile()
        self.label.setText(f"處理文件: {file_path}")
        self.process_file(file_path)

    def process_file(self, file_path : str):
        result : str = MyTranslator().tran2tw(file_path)
        self.save_file(content = result, original_name = file_path)

    def save_file(self, content : str, original_name : str = "translated.srt"):
        origin_file  = Path(original_name)
        org_suf      = origin_file.suffix
        default_name = origin_file.stem + "_tw" + org_suf
        file_name, _ = QFileDialog.getSaveFileName(self, caption = "保存文件", directory = default_name,filter = f"{org_suf} Files (*.{org_suf});;All Files (*)")
        if file_name:
            with open(file_name, 'w', encoding = "utf-8") as file:
                file.write(content)
                self.label.setText(f"文件已保存到: {file_name}\n你可以繼續拖放其他文件")

