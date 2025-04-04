import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QFileDialog, QVBoxLayout, QWidget
from PyQt6.QtCore    import Qt, QUrl
from PyQt6.QtGui     import QDragEnterEvent, QMouseEvent

from .translator import MyTranslator

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("  SRT簡體轉繁體，歐陽出品")
        self.setGeometry(100, 100, 600, 400)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout : QVBoxLayout= QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.label = QLabel("點擊任意地方來選擇檔案\nor\n把任何文字文件拖到这里\n\n我都會幫你轉換把簡體成繁體 !")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("font-size: 20px;")
        self.label.setAcceptDrops(True)
        # label client event
        self.label.mousePressEvent   = self.label_press_event
        self.label.mouseReleaseEvent = self.label_click_event
        self.label.dragEnterEvent    = self.label_dragEnterEvent
        self.label.dropEvent         = self.label_dropEvent

        self.layout.addWidget(self.label)
        

    def label_move_event(self, event : QMouseEvent):
        self.label.setStyleSheet("font-size: 20px; color: #d3b08d;")
    
    def label_press_event(self, event : QMouseEvent):
        self.label.setStyleSheet("font-size: 20px; color: #d3b08d;")

    def label_click_event(self, event : QMouseEvent):
        self.label.setStyleSheet("font-size: 20px; color: white;")
        # check if mouse release event is in label area
        if not self.label.rect().contains(event.pos()):
            return
        choose_file, _ = QFileDialog.getOpenFileNames(self, "選擇文件", "", "Text Files (*.txt *.srt);;All Files (*)")
        if not choose_file:
            return
        
        for each in choose_file:
            self.process_file(each)
        self.label.setText(f"已全部處理完畢\n你可以繼續拖放其他文件\nor\n把任何文字文件拖到这里")

    def label_dragEnterEvent(self, event : QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def label_dropEvent(self, event : QDragEnterEvent):
        Qurl_list : list[QUrl] = event.mimeData().urls()# [0].toLocalFile()
        for each in Qurl_list:
            file_path =  Path(each.toLocalFile())
            if file_path.suffix not in [".txt", ".srt"]:
                self.label.setText(f"文件 {file_path} 格式錯誤 !\n請選擇其他文件")
                print(f"文件 {file_path} 格式錯誤 !\n請選擇其他文件")
                continue
            if not file_path.exists():
                print(f"文件 {file_path} 不存在 !\n請選擇其他文件")
                continue
            self.process_file(file_path)
        self.label.setText(f"已全部處理完畢\n你可以繼續拖放其他文件\nor\n把任何文字文件拖到这里")
        self.label.setStyleSheet("font-size: 20px;")

    def process_file(self, file_path : str):
        self.label.setText(f"處理 {file_path} 中 ...")
        self.label.setStyleSheet("font-size: 20px;")
        result : str = MyTranslator().tran2tw(file_path)
        self.save_file(content = result, original_name = file_path)

    def save_file(self, content : str, original_name : str = "translated.srt"):
        origin_file  = Path(original_name)
        org_suf      = origin_file.suffix
        default_name = origin_file.stem + "_tw" + org_suf
        default_path = origin_file.parent / default_name
        file_name    = self.select_file(suffix = org_suf[1:] ,default_path = default_path)
        if file_name:
            with open(file_name, 'w', encoding = "utf-8") as file:
                file.write(content)
                self.label.setText(f"文件已保存到: {file_name}\n你可以繼續拖放其他文件\nor\n把任何文字文件拖到这里")

    def select_file(self, suffix : str, default_path : Path):
        file_name, _ = QFileDialog.getSaveFileName(self, caption = "保存文件", directory = str(default_path), filter = f"{suffix} Files (*.{suffix});;All Files (*)")
        return file_name

