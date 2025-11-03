# main.py
import sys
import os
import pandas as pd
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import QTimer, Qt, QPoint
from PyQt6.QtGui import QPixmap
from PyQt6.uic import loadUi

# ==== KLASÖR YOLLARI ==== #
BASE_DIR = os.path.dirname(__file__)
UI_DIR = os.path.join(BASE_DIR, "UI_s")
IMG_DIR = os.path.join(UI_DIR, "logo")
EXCEL_DIR = os.path.join(BASE_DIR, "Excels")

# ==== GLOBAL DEĞİŞKEN ==== #
last_window_pos = None  # Son pencere pozisyonunu saklamak için

# ==== BASE WINDOW ==== #
class BaseWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.oldPos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.oldPos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        import main  # global değişkeni güncel tutmak için        if event.buttons() == Qt.MouseButton.LeftButton:
        delta = event.globalPosition().toPoint() - self.oldPos
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPosition().toPoint()
        main.last_window_pos = self.pos()

    def move_to_last_position(self):
        import main
        if main.last_window_pos:
            self.move(main.last_window_pos)
        else:
            # İlk sefer için, mevcut konumu kaydet
            main.last_window_pos = self.pos()


# ==== SPLASH SCREEN ==== #
class SplashScreen(BaseWindow):
    def __init__(self):
        super().__init__()
        loadUi(os.path.join(UI_DIR, "Splash_Screen.ui"), self)
        self.setWindowTitle("CRM Splash Screen")
        self.setFixedSize(1000, 600)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.move_to_last_position()

        logo_path = os.path.join(IMG_DIR, "logo_butun.png")
        if os.path.exists(logo_path):
            self.label_logo.setPixmap(QPixmap(logo_path))
            self.label_logo.setScaledContents(True)

        self.counter = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(10)

    def update_progress(self):
        self.counter += 1
        self.progressBar.setValue(self.counter)
        if self.counter >= 100:
            self.timer.stop()
            self.show_login()

    def show_login(self):
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()


# ==== LOGIN WINDOW ==== #
class LoginWindow(BaseWindow):
    def __init__(self):
        super().__init__()
        loadUi(os.path.join(UI_DIR, "Login_Window.ui"), self)
        self.setWindowTitle("CRM Login")
        self.setFixedSize(1000, 600)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.move_to_last_position()

        logo_path = os.path.join(IMG_DIR, "logo_butun.png")
        if os.path.exists(logo_path):
            self.label.setPixmap(QPixmap(logo_path))
            self.label.setScaledContents(True)

        users_file = os.path.join(EXCEL_DIR, "users.xlsx")
        self.users_df = pd.read_excel(users_file)

        self.pushButton_Exit.clicked.connect(self.close)
        self.pushButton_Login.clicked.connect(self.login)

    def login(self):
        username = self.lineEdit_username.text()
        password = self.lineEdit_password.text()

        match = self.users_df[
            (self.users_df['username'] == username) &
            (self.users_df['password'] == password)
        ]

        if not match.empty:
            role = match.iloc[0]['role'].lower()
            print(f"Giriş başarılı! Rol: {role}")
            if role == "admin":
                self.dashboard = PreferenceAdminMenu(role=role)
            else:
                self.dashboard = PreferenceMenu(role=role)
            self.dashboard.show()
            self.close()
        else:
            print("Hatalı kullanıcı adı veya şifre.")

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.login()


# ==== ADMIN REEFERENCE MENU ==== #
class PreferenceAdminMenu(BaseWindow):
    def __init__(self, role="admin"):
        super().__init__()
        self.role = role
        loadUi(os.path.join(UI_DIR, "Preference_Admin_Menu.ui"), self)
        self.setWindowTitle("Admin Menu")
        self.setFixedSize(1000, 600)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.move_to_last_position()

        self.pushButton_INTERVIEWS.clicked.connect(self.open_interviews)
        self.pushButton_APPLICATIONS.clicked.connect(self.open_applications)
        self.pushButton_Mentor_Meeting.clicked.connect(self.open_mentor_meeting)
        self.pushButton_ADMIN_MENU.clicked.connect(self.open_admin_settings)
        self.pushButton_Return_Main_menu.clicked.connect(self.return_to_login)
        self.pushButton_Exit.clicked.connect(self.close)

    def open_interviews(self):
        from interviews_page import InterviewsWindow
        self.interviews_window = InterviewsWindow(role=self.role)
        self.interviews_window.show()
        self.close()

    def open_applications(self):
        from applications_page import ApplicationsWindow
        self.app_window = ApplicationsWindow(role=self.role)
        self.app_window.show()
        self.close()

    def open_mentor_meeting(self):
        from mentor_meeting_page import MentorMeetingWindow
        self.mentor_meeting_window = MentorMeetingWindow(role=self.role)
        self.mentor_meeting_window.show()
        self.close()

    def open_admin_settings(self):
        from admin_menu_page import AdminMenuWindow
        self.admin_menu = AdminMenuWindow(role=self.role)
        self.admin_menu.show()
        self.close()

    def return_to_login(self):
        self.login = LoginWindow()
        self.login.show()
        self.close()


# ==== USER REEFERENCE MENU ==== #
class PreferenceMenu(BaseWindow):
    def __init__(self, role="user"):
        super().__init__()
        self.role = role
        loadUi(os.path.join(UI_DIR, "Preference_Menu.ui"), self)
        self.setWindowTitle("User Menu")
        self.setFixedSize(1000, 600)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.move_to_last_position()

        if hasattr(self, "pushButton_INTERVIEWS"):
            self.pushButton_INTERVIEWS.clicked.connect(self.open_interviews)
        if hasattr(self, "pushButton_APPLICATIONS"):
            self.pushButton_APPLICATIONS.clicked.connect(self.open_applications)
        if hasattr(self, "pushButton_Mentor_Meeting"):
            self.pushButton_Mentor_Meeting.clicked.connect(self.open_mentor_meeting)
        if hasattr(self, "pushButton_Return_Main_menu"):
            self.pushButton_Return_Main_menu.clicked.connect(self.return_to_login)
        if hasattr(self, "pushButton_Exit"):
            self.pushButton_Exit.clicked.connect(self.close)

    def open_interviews(self):
        from interviews_page import InterviewsWindow
        self.interviews_window = InterviewsWindow(role=self.role)
        self.interviews_window.show()
        self.close()

    def open_applications(self):
        from applications_page import ApplicationsWindow
        self.app_window = ApplicationsWindow(role=self.role)
        self.app_window.show()
        self.close()

    def open_mentor_meeting(self):
        from mentor_meeting_page import MentorMeetingWindow
        self.mentor_meeting_window = MentorMeetingWindow(role=self.role)
        self.mentor_meeting_window.show()
        self.close()

    def return_to_login(self):
        self.login = LoginWindow()
        self.login.show()
        self.close()


# ==== MAIN ==== #
def main():
    app = QApplication(sys.argv)
    splash = SplashScreen()
    splash.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()