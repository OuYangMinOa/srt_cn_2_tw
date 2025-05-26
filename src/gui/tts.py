import asyncio
import hashlib
import os
import sys
import tempfile

from PyQt6.QtCore import QThread, Qt, pyqtSignal
from PyQt6.QtCore import QUrl, QTimer
from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer
from PyQt6.QtWidgets import (
    QProgressBar,
    QApplication,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
import edge_tts

# 語音合成執行緒
class TTSThread(QThread):
    finished = pyqtSignal(str)

    def __init__(self, text, voice, rate, pitch, output_path):
        super().__init__()
        self.text = text
        self.voice = voice
        self.rate = rate
        self.pitch = pitch
        self.output_path = output_path

    def run(self):
        asyncio.run(self._speak())

    async def _speak(self):
        try:
            communicate = edge_tts.Communicate(
                text=self.text,
                voice=self.voice,
                rate=f"{self.rate:+d}%" if self.rate != 1 else None,
                pitch=f"{self.pitch:+d}Hz" if self.pitch != 1 else None,
            )
            await communicate.save(self.output_path)
            self.finished.emit(self.output_path)
        except Exception as e:
            print(e)


class TTSWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.cache_dir = os.path.join(tempfile.gettempdir(), "tts_cache")
        os.makedirs(self.cache_dir, exist_ok=True)

        layout = QVBoxLayout()

        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("輸入要朗讀的文字...")
        layout.addWidget(self.text_edit)

        self.voice_box = QComboBox()
        self.voice_box.addItems([
            "zh-CN-XiaoxiaoNeural",         
            "zh-CN-XiaoyiNeural",           
            "zh-CN-YunjianNeural",          
            "zh-CN-YunxiNeural",            
            "zh-CN-YunxiaNeural",           
            "zh-CN-YunyangNeural",          
            "zh-CN-liaoning-XiaobeiNeural", 
            "zh-CN-shaanxi-XiaoniNeural",   
            "zh-TW-HsiaoChenNeural", 
            "zh-TW-HsiaoYuNeural",   
            "zh-TW-YunJheNeural"
        ])
        layout.addWidget(QLabel("選擇聲音"))
        layout.addWidget(self.voice_box)

        rate_layout = QHBoxLayout()
        rate_label = QLabel("語速（-100 到 100）")
        self.rate_value = QLabel("0%")
        rate_layout.addWidget(rate_label)
        rate_layout.addStretch()
        rate_layout.addWidget(self.rate_value)
        layout.addLayout(rate_layout)
        self.rate_slider = QSlider(Qt.Orientation.Horizontal)
        self.rate_slider.setMinimum(-100)
        self.rate_slider.setMaximum(100)
        self.rate_slider.setValue(0)
        self.rate_slider.valueChanged.connect(self.update_rate_label)
        layout.addWidget(self.rate_slider)

        pitch_layout = QHBoxLayout()
        pitch_label = QLabel("語調（-100 到 100）")
        self.pitch_value = QLabel("0%")
        pitch_layout.addWidget(pitch_label)
        pitch_layout.addStretch()
        pitch_layout.addWidget(self.pitch_value)
        layout.addLayout(pitch_layout)

        self.pitch_slider = QSlider(Qt.Orientation.Horizontal)
        self.pitch_slider.setMinimum(-100)
        self.pitch_slider.setMaximum(100)
        self.pitch_slider.setValue(0)
        self.pitch_slider.valueChanged.connect(self.update_pitch_label)
        layout.addWidget(self.pitch_slider)

        # 按鈕列
        btn_layout = QHBoxLayout()
        self.play_button = QPushButton("▶ 播放")
        self.play_button.clicked.connect(self.play_audio)
        btn_layout.addWidget(self.play_button)
        self.save_button = QPushButton("💾 儲存語音")
        self.save_button.clicked.connect(self.save_audio)
        btn_layout.addWidget(self.save_button)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

        # 播放進度條
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar::chunk {
                background-color: #4CAF50;  /* 綠色 */
            }
        """)
        layout.addWidget(self.progress_bar)

        # 播放控制與定時器
        self.audio_output = QAudioOutput()
        self.player = QMediaPlayer()
        self.player.setAudioOutput(self.audio_output)

        self.player.positionChanged.connect(self.update_progress)
        self.player.durationChanged.connect(self.set_progress_range)
        self.player.mediaStatusChanged.connect(self.on_media_status_changed)

        self.timer = QTimer()
        self.timer.setInterval(100)  # 每 100ms 更新一次
        self.timer.timeout.connect(self.update_progress_bar)

        self.is_playing = False

    def update_rate_label(self, value):
        self.rate_value.setText(f"{value:+d}%")

    def update_pitch_label(self, value):
        self.pitch_value.setText(f"{value:+d}%")

    def get_current_cache_path(self):
        text = self.text_edit.toPlainText()
        voice = self.voice_box.currentText()
        rate = self.rate_slider.value()
        pitch = self.pitch_slider.value()

        key = f"{voice}_{rate}_{pitch}_{text}".encode("utf-8")
        hash_name = hashlib.md5(key).hexdigest()
        return os.path.join(self.cache_dir, f"{hash_name}.mp3")

    def generate_tts(self, path, callback=None):
        text = self.text_edit.toPlainText()
        voice = self.voice_box.currentText()
        rate = self.rate_slider.value()
        pitch = self.pitch_slider.value()

        self.thread = TTSThread(text, voice, rate, pitch, path)
        if callback:
            self.thread.finished.connect(callback)
        self.thread.start()

    def play_audio(self):
        if self.is_playing:
            self.player.pause()
            self.play_button.setText("▶ 播放")
            self.is_playing = False
            self.timer.stop()
            return

        cache_path = self.get_current_cache_path()

        if os.path.exists(cache_path):
            self._start_playback(cache_path)
        else:
            self.play_button.setText("⏳ 產生中...")
            self.generate_tts(cache_path, self.on_play_ready)

    def _play(self, path):
        self.player.setSource(QUrl.fromLocalFile(path))
        self.player.play()

    def _start_playback(self, path):
        if self.is_playing:
            self.player.stop()
        else:
            self.player.setSource(QUrl.fromLocalFile(path))
            self.player.play()
            self.play_button.setText("⏸ 暫停")
            self.is_playing = True
            self.timer.start()

    def on_play_ready(self, path):
        self.play_button.setText("▶ 播放")
        self._start_playback(path)

    def update_progress(self, position):
        if self.player.duration() > 0:
            progress = int((position / self.player.duration()) * 100)
            self.progress_bar.setValue(progress)

    def set_progress_range(self, duration):
        if duration > 0:
            self.progress_bar.setMaximum(100)

    def update_progress_bar(self):
        self.update_progress(self.player.position())

    def on_media_status_changed(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.play_button.setText("▶ 播放")
            self.progress_bar.setValue(0)
            self.is_playing = False
            self.timer.stop()

    def save_audio(self):
        cache_path = self.get_current_cache_path()
        if os.path.exists(cache_path):
            self._save_file(cache_path)
        else:
            self.save_button.setText("⏳ 產生中...")
            self.generate_tts(cache_path, self._save_file)

    def _save_file(self, path):
        self.save_button.setText("💾 儲存語音")
        save_path, _ = QFileDialog.getSaveFileName(self, "儲存語音", "output", "Audio Files (*.mp3)")
        if save_path:
            with open(path, "rb") as src, open(save_path, "wb") as dst:
                dst.write(src.read())
