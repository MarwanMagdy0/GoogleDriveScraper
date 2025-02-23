from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QIcon

import sqlite3
import hashlib


conn = sqlite3.connect('database.db')
cursor = conn.cursor()

class WorkspaceSettingsTable:
    @staticmethod
    def is_admin(password):
        cursor.execute("""
            SELECT setting_value 
            FROM workspace_settings 
            WHERE setting_key = 'admin_password';
        """)
        result = cursor.fetchone()
        
        if result:
            return hashlib.sha256(password.encode('utf-8')).hexdigest() == result[0]
        return None
    
def show_info_box(info_title, info_content, icon=QMessageBox.Warning):
    msg_box = QMessageBox()
    msg_box.setWindowTitle(info_title)  # Title of the info box
    msg_box.setText(info_content)  # Message to display
    msg_box.setIcon(icon)  # Icon for the message box
    msg_box.setWindowIcon(QIcon(":/Images/quickspace.png"))
    msg_box.setStandardButtons(QMessageBox.Ok)  # Button to close the box
    msg_box.exec_()

if __name__ == "__main__":
    print(WorkspaceSettingsTable.is_admin("admin"))