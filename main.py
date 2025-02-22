from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidget, QLineEdit, QProgressBar, QPushButton, QListWidgetItem
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSettings
from google_drive_api import GoogleDriveAPI, is_connected_to_internet
from resources.ui_scripts.load import Ui_MainWindow

import os
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

class FetchDataThread(QThread):
    dataFetched = pyqtSignal(dict)

    def __init__(self, link):
        super().__init__()
        self.link = link

    def run(self):
        files = GoogleDriveAPI.list_files(self.link)
        self.dataFetched.emit(files)


class DownloadThread(QThread):
    progress = pyqtSignal(int)  # Signal for progress updates
    completed = pyqtSignal()  # Signal when the download is complete
    failed = pyqtSignal()  # Signal on failure

    def __init__(self, file_id, file_name):
        super().__init__()
        self.file_id = file_id
        self.file_name = file_name

    def run(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        first_emit_done = False
        for progress_value in GoogleDriveAPI.download_file(self.file_id, self.file_name):
            if progress_value is None:
                self.failed.emit()
                return
            if not first_emit_done:
                QApplication.restoreOverrideCursor()
                first_emit_done = True
            self.progress.emit(progress_value)

        self.completed.emit()  # Emit completion signal


class MainWindow(QMainWindow, Ui_MainWindow):
    link_lineedit: QLineEdit
    update_listwidget_pushbutton: QPushButton
    download_button: QPushButton
    listWidget: QListWidget
    progressBar: QProgressBar

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.progressBar.setValue(0)

        self.settings = QSettings("QuickSpace", "quickspace")  # Replace with your app details

        # Load the saved link from settings
        self.load_settings()

        self.update_listwidget_pushbutton.clicked.connect(self.update_list)
        self.download_button.clicked.connect(self.start_download)

    def load_settings(self):
        saved_link = self.settings.value("drive_link", "")
        self.link_lineedit.setText(saved_link)

    def save_settings(self):
        self.settings.setValue("drive_link", self.link_lineedit.text())

    def update_list(self):
        if not is_connected_to_internet():
            return
        
        def update_listwidget(files):
            self.listWidget.clear()
            for file_id, file_name in files.items():
                item = QListWidgetItem(file_name)
                item.setTextAlignment(Qt.AlignCenter)
                item.setData(Qt.UserRole, file_id)
                self.listWidget.addItem(item)
            
            self.download_button.setEnabled(True)
            QApplication.restoreOverrideCursor()

        link = self.link_lineedit.text()
        if link == "":
            return
        
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.fetch_data_thread = FetchDataThread(link)
        self.fetch_data_thread.dataFetched.connect(update_listwidget)
        self.fetch_data_thread.start()
    
    def start_download(self):
        if not is_connected_to_internet():
            return
        def download_completed():
            self.progressBar.setValue(0)
            if self.listWidget.count() > 0:
                self.listWidget.takeItem(0)
                self.start_download() # start fetching other files

        if self.listWidget.count() == 0:
            return
        
        file_id = self.listWidget.item(0).data(Qt.UserRole)
        file_name = self.listWidget.item(0).text()
        self.download_thread = DownloadThread(file_id, file_name)
        self.download_thread.progress.connect(self.progressBar.setValue)
        self.download_thread.completed.connect(download_completed)
        self.download_thread.failed.connect(lambda name: self.progressBar.setValue(0))
        self.download_thread.start()
    
    def closeEvent(self, event):
        self.save_settings()
        event.accept()

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
