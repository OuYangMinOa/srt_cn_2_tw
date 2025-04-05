import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QFileDialog, QVBoxLayout, QWidget, QHBoxLayout, QTextEdit
from PyQt6.QtCore    import Qt, QUrl
from PyQt6.QtGui     import QDragEnterEvent, QMouseEvent

from .translator import MyTranslator

class MainWindow(QMainWindow):
    LABEL_SYTLE = "border: 2px solid white; border-radius: 5px;font-size: 20px;"
    def __init__(self):
        super().__init__()

        self.mytrans_cn2tw = MyTranslator()
        self.mytrans_tw2cn = MyTranslator(mode = "tw2s")
        self.setup_gui()

    def setup_gui(self):
        self.setWindowTitle("  SRT簡體轉繁體，歐陽出品")
        self.setGeometry(100, 100, 600, 400)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self._layout = QVBoxLayout()
        self.central_widget.setLayout(self._layout)

        self.label = QLabel("點擊任意地方來選擇檔案\nor\n把任何文字文件拖到这里\n\n我都會幫你轉換把簡體成繁體 !")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet(self.LABEL_SYTLE)
        self.label.setAcceptDrops(True)
        self._layout.addWidget(self.label)

        # 添加一個水平佈局來放置兩個輸入框
        self.input_layout = QHBoxLayout()

        # 創建左側的輸入框
        self.use_left_input_event = True
        self.left_input = QTextEdit()
        self.left_input.setPlaceholderText("輸入簡體")
        self.left_input.textChanged.connect(self.left_input_event)
        self.input_layout.addWidget(self.left_input)

        # 創建右側輸 繁體
        self.use_right_input_event = True
        self.right_input = QTextEdit()
        self.right_input.setPlaceholderText("得到繁體")
        self.right_input.textChanged.connect(self.right_input_event)
        self.input_layout.addWidget(self.right_input)

        # 設置輸入框的滾動條同步
        self.right_input.verticalScrollBar().valueChanged.connect(self.left_input.verticalScrollBar().setValue)
        self.right_input.horizontalScrollBar().valueChanged.connect(self.left_input.horizontalScrollBar().setValue)
        self.left_input.verticalScrollBar().valueChanged.connect(self.right_input.verticalScrollBar().setValue)
        self.left_input.horizontalScrollBar().valueChanged.connect(self.right_input.horizontalScrollBar().setValue)

        self._layout.addLayout(self.input_layout)

        self.button_layout = QHBoxLayout()
        self.button_layout.addStretch()
        self._layout.addLayout(self.button_layout)

        # label client event
        self.label.mousePressEvent   = self.label_press_event
        self.label.mouseReleaseEvent = self.label_click_event
        self.label.dragEnterEvent    = self.label_dragEnterEvent
        self.label.dropEvent         = self.label_dropEvent

    def left_input_event(self):
        if not self.use_left_input_event:
            return
        content = self.left_input.toPlainText()
        if content == "":
            return
        result : str = self.mytrans_cn2tw.tran2tw(content)
        self.use_right_input_event = False
        self.right_input.setText(result)
        self.use_right_input_event = True

    def right_input_event(self):
        if not self.use_right_input_event:
            return
        content = self.right_input.toPlainText()
        if content == "":
            return
        result : str = self.mytrans_tw2cn.tran2tw(content)
        self.use_left_input_event = False
        self.left_input.setText(result)
        self.use_left_input_event = True

    def label_move_event(self, event : QMouseEvent):
        self.label.setStyleSheet(self.LABEL_SYTLE + "color: #d3b08d;")
    
    def label_press_event(self, event : QMouseEvent):
        self.label.setStyleSheet(self.LABEL_SYTLE + "color: #d3b08d;")

    def label_click_event(self, event : QMouseEvent):
        self.label.setStyleSheet(self.LABEL_SYTLE +  "color: white;")
        # check if mouse release event is in label area
        if not self.label.rect().contains(event.pos()):
            return
        choose_file, _ = QFileDialog.getOpenFileNames(self, "選擇文件", "", "Text Files (*.txt *.srt);;All Files (*)")
        if not choose_file:
            return
        
        for each in choose_file:
            self.process_file(each)
        self.label.setText(f"已全部處理完畢\n\n你可以繼續拖放其他文件\nor\n點擊任意地方來選擇檔案")

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
        self.label.setText(f"已全部處理完畢\n\n你可以繼續拖放其他文件\nor\n點擊任意地方來選擇檔案")
        self.label.setStyleSheet(self.LABEL_SYTLE)

    def process_file(self, file_path : str):
        self.label.setText(f"處理 {file_path} 中 ...")
        self.label.setStyleSheet(self.LABEL_SYTLE)
        content : str = self.mytrans_cn2tw.read_file(file_path)
        self.use_left_input_event  = False
        self.use_right_input_event = False
        self.left_input.setText(content)
        result : str = self.mytrans_cn2tw.tran2tw(content)
        self.right_input.setText(result)
        self.use_left_input_event  = True
        self.use_right_input_event = True
        total_lines = len(result.split("\n"))
        self.label.setText(f"處理 {file_path} 完成 !\n一共 {total_lines} 行\n\n請選擇保存文件的路徑")
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
                self.label.setText(f"文件已保存到: {file_name}\n\n你可以繼續拖放其他文件\nor\n點擊任意地方來選擇檔案")

    def select_file(self, suffix : str, default_path : Path):
        file_name, _ = QFileDialog.getSaveFileName(self, caption = "保存文件", directory = str(default_path), filter = f"{suffix} Files (*.{suffix});;All Files (*)")
        return file_name

