from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from api.google_drive_api import GoogleDriveAPI

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
