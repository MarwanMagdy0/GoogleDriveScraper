from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QProgressBar, QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt
from api.google_drive_api import is_connected_to_internet
from api.google_drive_interface import FetchDataThread, DownloadThread
from scripts.utiles import show_info_box
from resources.ui_scripts.load import Ui_MainWindow

import os

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

URL = "https://drive.google.com/drive/u/0/folders/1E4JiVhXLIi4J-ceO0BjqVu8ll3fw-r25"  # Arabesque


class MainWindow(QMainWindow, Ui_MainWindow):
    progressBar: QProgressBar
    download_button: QPushButton

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.new_version_data = None
        self.progressBar.setValue(0)
        self.download_button.setEnabled(False)
        self.download_button.clicked.connect(self.start_download)

        self.init_fetch_links()

    def init_fetch_links(self):
        if not is_connected_to_internet():
            show_info_box("Offline", "No internet connection available.")
            return

        QApplication.setOverrideCursor(Qt.WaitCursor)

        def link_fetched(download_links):
            QApplication.restoreOverrideCursor()
            if not download_links:
                show_info_box("No Update", "No new version available.")
                return
            self.new_version_data = download_links
            self.download_button.setEnabled(True)
            self.start_download()  # Start immediately without user click

        self.fetch_data_thread = FetchDataThread(URL)
        self.fetch_data_thread.dataFetched.connect(link_fetched)
        self.fetch_data_thread.start()

    def start_download(self):
        if not self.new_version_data:
            return

        file_id = list(self.new_version_data.keys())[0]
        file_name = self.new_version_data[file_id]

        def download_completed():
            self.progressBar.setValue(0)
            self.download_button.setEnabled(False)
            show_info_box("Update completed", "Please restart the application.", QMessageBox.Information)
            QApplication.quit()

        self.download_thread = DownloadThread(file_id, file_name)
        self.download_thread.progress.connect(self.progressBar.setValue)
        self.download_thread.completed.connect(download_completed)
        self.download_thread.failed.connect(lambda name: self.progressBar.setValue(0))
        self.download_thread.start()


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
