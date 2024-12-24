import os
import subprocess
import sys
from pathlib import Path
from typing import Optional
from logging import getLogger

import yt_dlp
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QLineEdit, QPushButton, QFileDialog, QMessageBox, QProgressBar

)

logger = getLogger(__name__)


class YoutubeDownloader(QWidget):
    def __init__(self):
        super().__init__()

        self.catalog: Optional[str | Path] = Path.cwd() / 'videos'
        self.catalog.mkdir(exist_ok=True)

        self.url_input: Optional[QLineEdit] = None
        self.url_label: Optional[QLabel] = None
        self.catalog_label: Optional[QLabel] = None
        self.status_label: Optional[QLabel] = None
        self.catalog_button: Optional[QPushButton] = None
        self.download_button: Optional[QPushButton] = None
        self.progress_bar: Optional[QProgressBar] = None

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Vifania Youtube Downloader")
        self.resize(400, 200)

        layout = QVBoxLayout(self)

        self.url_label = QLabel("Введите URL видео с youtube.com")
        layout.addWidget(self.url_label)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://www.youtube.com/watch?v=...")
        self.url_input.setText('https://www.youtube.com/watch?v=HvZab3jmvQA')
        layout.addWidget(self.url_input)

        self.catalog_button = QPushButton("Выбрать путь сохранения")
        self.catalog_button.clicked.connect(self.choose_catalog)
        layout.addWidget(self.catalog_button)

        self.catalog_label = QLabel(f"Выбран путь: {self.catalog}")
        layout.addWidget(self.catalog_label)

        self.download_button = QPushButton("Скачать")
        self.download_button.clicked.connect(self.download_video)
        layout.addWidget(self.download_button)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def choose_catalog(self):
        catalog = QFileDialog.getExistingDirectory()
        if catalog:
            self.catalog = catalog
            self.catalog_label.setText(f"Выбран путь: {catalog}")

    def update_progress(self, progress):
        if progress["status"] == "downloading":
            downloaded = progress.get("downloaded_bytes", 0)
            total = progress.get("total_bytes", progress.get("total_bytes_estimate", 1))
            percentage = int(downloaded / total * 100)
            self.progress_bar.setValue(percentage)
        elif progress["status"] == "finished":
            self.progress_bar.setValue(100)
            self.status_label.setText("Download finished. Processing...")

    def download_video(self):
        url = self.url_input.text()

        if not url:
            QMessageBox.warning(self, "Ошибка пути", "Пожалуйста, укажите URL видео для скачивания!")
            return
        if 'https' not in url:
            QMessageBox.warning(self, "Ошибка пути", "Пожалуйста, укажите корректный URL видео для скачивания!")
            return

        self.status_label.setText("Скачивание...")
        self.progress_bar.setValue(0)
        self.status_label.repaint()

        ydl_opts = {
            "format": "bestvideo+bestaudio/best",
            "merge_output_format": "mp4",
            "progress_hooks": [self.update_progress],
            'outtmpl': self.catalog.__str__() + '/%(title)s.%(ext)s',
            'ffmpeg_location': 'ffmpeg/bin/ffmpeg.exe',
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                downloaded_file = os.path.abspath(ydl.prepare_filename(info))

            self.status_label.setText("Загрузка завершена!")
            run_command = ["explorer", "/select,", f'{downloaded_file}']
            print(run_command)
            subprocess.run(run_command)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка при скачивании видео! {e.__str__()}")
            return


if __name__ == "__main__":
    app = QApplication(sys.argv)
    downloader = YoutubeDownloader()
    downloader.show()
    sys.exit(app.exec())
