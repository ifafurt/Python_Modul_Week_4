import os
from PyQt6.uic import loadUi
from PyQt6.QtCore import Qt
from main import BaseWindow

BASE_DIR = os.path.dirname(__file__)
UI_DIR = os.path.join(BASE_DIR, "UI_s")

class MentorMeetingWindow(BaseWindow):
    def __init__(self, role="admin"):
        super().__init__()
        self.role = role
        loadUi(os.path.join(UI_DIR, "Mentor_Meeting_Page.ui"), self)
        self.setWindowTitle("Mentor Meeting Page")
        self.setFixedSize(1000, 600)
        self.move_to_last_position()

        self.pushButton_Return_REFERENCE_menu.clicked.connect(self.return_to_menu)
        self.pushButton_EXIT.clicked.connect(self.close)
        self.pushButton_SEARCH.clicked.connect(self.search_action)

    def return_to_menu(self):
        from main import PreferenceAdminMenu, PreferenceMenu
        if self.role.lower() == "admin":
            self.pref_menu = PreferenceAdminMenu(role=self.role)
        else:
            self.pref_menu = PreferenceMenu(role=self.role)
        self.pref_menu.show()
        self.close()

    def search_action(self):
        text = self.lineEdit.text().strip()
        print(f"🔍 Mentor Meeting search: {text}")