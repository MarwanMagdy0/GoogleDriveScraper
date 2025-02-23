from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QProgressBar, QPushButton, QListWidgetItem, QStackedWidget, QMessageBox
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSettings
from api.google_drive_api import is_connected_to_internet
from api.google_drive_interface import FetchDataThread, DownloadThread
from scripts.utiles import WorkspaceSettingsTable, show_info_box
from resources.ui_scripts.load import Ui_MainWindow

import os
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

URL = "https://drive.google.com/drive/u/0/folders/1E4JiVhXLIi4J-ceO0BjqVu8ll3fw-r25"

class UI(QMainWindow, Ui_MainWindow):
    stackedWidget : QStackedWidget

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.new_version_data = None


class LoginPage(UI):
    password_lineedit: QLineEdit
    download_button: QPushButton

    def __init__(self):
        super().__init__()
        
        self.password_lineedit.returnPressed.connect(self.check_password)
    
    def check_password(self):
        def link_fetched(download_links):
            QApplication.restoreOverrideCursor()
            if len(download_links) == 0:
                show_info_box("No new version available", "Please try again later.")
                return
            
            self.new_version_data = download_links
            self.download_button.setEnabled(True)

        password = self.password_lineedit.text()
        if WorkspaceSettingsTable.is_admin(password):
            self.stackedWidget.setCurrentIndex(1)
            QApplication.setOverrideCursor(Qt.WaitCursor)
            self.fetch_data_thread = FetchDataThread(URL)
            self.fetch_data_thread.dataFetched.connect(link_fetched)
            self.fetch_data_thread.start()

        self.password_lineedit.setText("")


class DownloadPage(UI):
    download_button: QPushButton
    progressBar: QProgressBar
    def __init__(self):
        super().__init__()
        self.progressBar.setValue(0)
        self.download_button.clicked.connect(self.start_download)
    
    def start_download(self):
        print(self.new_version_data)
        if not is_connected_to_internet():
            return
        def download_completed():
            self.progressBar.setValue(0)
            self.download_button.setEnabled(False)
            show_info_box("Update completed", "Please restart the application.", QMessageBox.Information)
            self.stackedWidget.setCurrentIndex(0)    
    
        file_id = list(self.new_version_data.keys())[0]
        file_name = self.new_version_data[file_id]
        self.download_thread = DownloadThread(file_id, file_name)
        self.download_thread.progress.connect(self.progressBar.setValue)
        self.download_thread.completed.connect(download_completed)
        self.download_thread.failed.connect(lambda name: self.progressBar.setValue(0))
        self.download_thread.start()

class BuildMainWindow(LoginPage, DownloadPage):
    def __init__(self):
        super().__init__()

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = BuildMainWindow()
    window.show()
    sys.exit(app.exec_())
