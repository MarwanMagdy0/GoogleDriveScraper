from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QIcon
from datetime import datetime
import traceback
import logging
import sys, os

    
def show_info_box(info_title, info_content, icon=QMessageBox.Warning):
    msg_box = QMessageBox()
    msg_box.setWindowTitle(info_title)  # Title of the info box
    msg_box.setText(info_content)  # Message to display
    msg_box.setIcon(icon)  # Icon for the message box
    msg_box.setWindowIcon(QIcon(":/Images/quickspace.png"))
    msg_box.setStandardButtons(QMessageBox.Ok)  # Button to close the box
    msg_box.exec_()

class Logger:
    @staticmethod
    def logIntoFile(file_name):
        # Create the root logger and set its level to DEBUG
        logger = logging.getLogger("Arabesque")
        logger.setLevel(logging.DEBUG)
        
        # Create a file handler and set its level to INFO
        file_handler = logging.FileHandler(file_name)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        
        # Add handlers to the logger
        logger.addHandler(file_handler)
        
        # Set custom exception hook to handle uncaught exceptions
        sys.excepthook = Logger.handle_exception

    @staticmethod
    def handle_exception(exc_type, exc_value, exc_traceback):
        # Log unhandled exceptions with traceback
        logger = logging.getLogger("Arabesque")
        logger.error(f'Unhandled exception: {exc_type.__name__}: {exc_value}')
        logger.error("".join(traceback.format_tb(exc_traceback)))
        sys.__excepthook__(exc_type, exc_value, exc_traceback)

os.makedirs("logs", exist_ok=True)
log_file_name = f"{datetime.now().strftime('%Y-%m-%d')}_app.log"
Logger.logIntoFile(os.path.join("logs", log_file_name))
