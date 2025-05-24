from __future__ import annotations
from pathlib import Path
import sys

from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QFileDialog, QVBoxLayout, QWidget, QHBoxLayout, QTextEdit, QComboBox
from PyQt6.QtCore    import Qt, QUrl
from PyQt6.QtGui     import QDragEnterEvent, QMouseEvent

from .translator import MyTranslator, MyTranslator2
from enum import Enum


class Lang(Enum):
    EN = 'en'
    TW = 'zh-TW'
    CN = 'zh-CN'

    @classmethod
    def from_str(cls, string : str) -> Lang:
        if string == "英文":
            return Lang.EN

        if string == "繁體":
            return Lang.TW

        if string == "簡體":
            return Lang.CN

        raise Exception("Unsupport language")

class MainWindow(QMainWindow):
    LABEL_SYTLE = "border: 2px solid white; border-radius: 5px;font-size: 20px;"
    def __init__(self):
        super().__init__()
        self.final_filepath = "translated.srt"
        self.mytrans_cn2tw  = MyTranslator()
        self.mytrans_tw2cn  = MyTranslator(mode = "tw2s")
        self.mytrans_2en    = MyTranslator2()
        self.setup_gui()

    def setup_gui(self):
        self.setWindowTitle("  SRT簡體轉繁體，歐陽出品")
        self.setGeometry(100, 100, 600, 400)

        self.central_widget : QWidget = QWidget()
        self.setCentralWidget(self.central_widget)
        self._layout = QVBoxLayout()
        self.central_widget.setLayout(self._layout)

        self.label = QLabel("點擊這裡來選擇檔案\nor\n把任何文字文件拖到这里\n\n我都會幫你轉換把簡體成繁體 !")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet(self.LABEL_SYTLE)
        self.label.setAcceptDrops(True)
        # label client event
        self.label.mousePressEvent   = self.label_press_event
        self.label.mouseReleaseEvent = self.label_click_event
        self.label.dragEnterEvent    = self.label_dragEnterEvent
        self.label.dropEvent         = self.label_dropEvent
        self._layout.addWidget(self.label)

        self.combo_left = QComboBox()
        self.combo_left.addItems(["簡體","繁體","英文" ])

        self.combo_right = QComboBox()
        self.combo_right.addItems(["繁體","英文", "簡體"])

        h_layout = QHBoxLayout()
        h_layout.addWidget(self.combo_left)
        h_layout.addWidget(self.combo_right)

        self._layout.addLayout(h_layout)


        # 添加一個水平佈局來放置兩個輸入框
        self.input_layout = QHBoxLayout()

        # 創建左側的輸入框
        self.left_input = QTextEdit()
        self.left_input.setPlaceholderText("輸入")
        self.input_layout.addWidget(self.left_input)

        # 創建右側輸 繁體
        self.right_input = QTextEdit()
        self.right_input.setPlaceholderText("得到繁體")
        self.input_layout.addWidget(self.right_input)

        # 設置輸入框的滾動條同步
        self.right_input.verticalScrollBar().valueChanged.connect(self.left_input.verticalScrollBar().setValue)
        self.right_input.horizontalScrollBar().valueChanged.connect(self.left_input.horizontalScrollBar().setValue)
        self.left_input.verticalScrollBar().valueChanged.connect(self.right_input.verticalScrollBar().setValue)
        self.left_input.horizontalScrollBar().valueChanged.connect(self.right_input.horizontalScrollBar().setValue)

        self._layout.addLayout(self.input_layout)


        self.clear_convert_button = QHBoxLayout()
        # 清除
        self.clear_button = QLabel("清除")
        self.clear_button.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.clear_button.setStyleSheet(self.LABEL_SYTLE)
        self.clear_convert_button.addWidget(self.clear_button)
        self.clear_button.mousePressEvent   = self.clear_button_press
        self.clear_button.mouseReleaseEvent = self.clear_button_click_event
        # 轉換
        self.convert_button = QLabel("轉換")
        self.convert_button.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.convert_button.setStyleSheet(self.LABEL_SYTLE)
        self.clear_convert_button.addWidget(self.convert_button)
        self.convert_button.mousePressEvent   = self.convert_button_press
        self.convert_button.mouseReleaseEvent = self.convert_button_click_event
        # label client event
        self._layout.addLayout(self.clear_convert_button)



        self.button_layout = QHBoxLayout()
        self.save_button = QLabel("保存文件")
        self.save_button.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.save_button.setStyleSheet(self.LABEL_SYTLE)
        self.button_layout.addWidget(self.save_button)
        # label client event
        self.save_button.mousePressEvent   = self.save_button_press_event
        self.save_button.mouseReleaseEvent = self.save_button_click_event
        self._layout.addLayout(self.button_layout)

    def clear_button_press(self, event : QMouseEvent):
        self.clear_button.setStyleSheet(self.LABEL_SYTLE + "color: #d3b08d;")

    def clear_button_click_event(self, event : QMouseEvent):
        self.clear_button.setStyleSheet(self.LABEL_SYTLE + "color: white;")

    def convert_button_press(self, event : QMouseEvent):
        self.convert_button.setStyleSheet(self.LABEL_SYTLE + "color: #d3b08d;")

    def convert_button_click_event(self, event : QMouseEvent):
        self.convert_button.setStyleSheet(self.LABEL_SYTLE + "color: white;")

    def save_button_click_event(self, event : QMouseEvent):
        self.save_button.setStyleSheet(self.LABEL_SYTLE + "color: white;")
        # check if mouse release event is in label area
        if not self.label.rect().contains(event.pos()):
            return
        save_content = self.right_input.toPlainText()
        if save_content == "":
            return
        self.save_file(content = save_content, original_name = self.final_filepath)
        
    def save_button_press_event(self, event : QMouseEvent):
        self.save_button.setStyleSheet(self.LABEL_SYTLE + "color: #d3b08d;")
    
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
        self.label.setText(f"已全部處理完畢\n\n你可以繼續拖放其他文件\nor\n點擊這裡來選擇檔案")

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
        self.label.setText(f"已全部處理完畢\n\n你可以繼續拖放其他文件\nor\n點擊這裡來選擇檔案")
        self.label.setStyleSheet(self.LABEL_SYTLE)

    def process_file(self, file_path : str, show_progress : bool = True):
        self.label.setText(f"處理 {file_path} 中 ...")
        self.final_filepath = file_path
        self.label.setStyleSheet(self.LABEL_SYTLE)
        raw_text : str = self.mytrans_cn2tw.read_file(file_path)
        self.left_input.setText(raw_text)
        translated_text : str = self.mytrans_cn2tw.translate(raw_text, show_progress = show_progress)
        self.right_input.setText(translated_text)
        total_lines = len(translated_text.split("\n"))
        self.label.setText(f"處理 {file_path} 完成 !\n一共 {total_lines} 行\n\n請選擇保存文件的路徑")
        self.save_file(content = translated_text, original_name = file_path)

    def save_file(self, content : str, original_name : str = "translated.srt"):
        origin_file  = Path(original_name)
        org_suf      = origin_file.suffix
        default_name = origin_file.stem + "_tw" + org_suf
        default_path = origin_file.parent / default_name
        file_name    = self.select_file(suffix = org_suf[1:] ,default_path = default_path)
        if file_name:
            with open(file_name, 'w', encoding = "utf-8") as file:
                file.write(content)
                self.label.setText(f"文件已保存到: {file_name}\n\n你可以繼續拖放其他文件\nor\n點擊這裡來選擇檔案")

    def select_file(self, suffix : str, default_path : Path):
        file_name, _ = QFileDialog.getSaveFileName(self, caption = "保存文件", directory = str(default_path), filter = f"{suffix} Files (*.{suffix});;All Files (*)")
        return file_name

