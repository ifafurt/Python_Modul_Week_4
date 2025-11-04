# interviews_page.py

import os
from PyQt6.uic import loadUi
from PyQt6.QtCore import Qt
from main import BaseWindow
from PyQt6 import QtWidgets

BASE_DIR = os.path.dirname(__file__)
UI_DIR = os.path.join(BASE_DIR, "UI_s")


class InterviewsWindow(BaseWindow):
    def __init__(self, role="admin"):
        super().__init__()
        self.role = role
        loadUi(os.path.join(UI_DIR, "Interviews.ui"), self)
        self.setWindowTitle("Interviews")
        self.setFixedSize(1000, 600)
        self.move_to_last_position()

        # Butonları bağla
        self.pushButton_Return_REFERENCE_menu.clicked.connect(self.return_to_menu)
        self.pushButton_EXIT.clicked.connect(self.close)
        self.pushButton_SEARCH.clicked.connect(self.search_action)
        self.pushButton_SUBMITTED_PROJECTS.clicked.connect(self.show_submitted_projects)
        self.pushButton_RECEIVED_PROJECTS.clicked.connect(self.show_received_projects)

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
        print(f"🔍 Searching for: {text}")

    def show_submitted_projects(self):
        print("📤 Showing submitted projects...")

    def show_received_projects(self):
        print("📥 Showing received projects...")
