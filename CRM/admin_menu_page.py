import os
from PyQt6.uic import loadUi
from PyQt6.QtCore import Qt
from main import BaseWindow

BASE_DIR = os.path.dirname(__file__)
UI_DIR = os.path.join(BASE_DIR, "UI_s")

class AdminMenuWindow(BaseWindow):
    def __init__(self, role="admin"):
        super().__init__()
        self.role = role
        loadUi(os.path.join(UI_DIR, "Admin_Menu.ui"), self)
        self.setWindowTitle("Admin Menu")
        self.setFixedSize(1000, 600)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.move_to_last_position()

        self.pushButton_SEND_EMAIL.clicked.connect(self.send_email)
        self.pushButton_EVENT_REGISTRATION.clicked.connect(self.register_event)
        self.pushButton_Return_TO_ADMIN_PREFERENCE_menu.clicked.connect(self.return_to_admin_pref_menu)
        self.pushButton_Exit.clicked.connect(self.close)

    def send_email(self):
        print("📧 Send Email clicked")

    def register_event(self):
        print("🗓 Event Registration clicked")

    def return_to_admin_pref_menu(self):
        from main import PreferenceAdminMenu
        self.pref_menu = PreferenceAdminMenu(role=self.role)
        self.pref_menu.show()
        self.close()