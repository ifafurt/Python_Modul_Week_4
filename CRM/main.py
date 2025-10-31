import sys
import os
import pandas as pd
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QLabel
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QPixmap
from PyQt6.uic import loadUi

# Klasör yolları
BASE_DIR = os.path.dirname(__file__)
UI_DIR = os.path.join(BASE_DIR, "UI_s")
IMG_DIR = os.path.join(UI_DIR, "logo")
EXCEL_DIR = os.path.join(BASE_DIR, "Excels")

class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        splash_ui_path = os.path.join(UI_DIR, "Splash_Screen.ui")
        loadUi(splash_ui_path, self)
        self.setWindowTitle("CRM Splash Screen")
        self.setFixedSize(1000, 600)

        # Logo yükleme
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


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        login_ui_path = os.path.join(UI_DIR, "Login_Window.ui")
        loadUi(login_ui_path, self)
        self.setWindowTitle("CRM Login")
        self.setFixedSize(1000, 600)

        # Excel'den kullanıcıları oku
        users_file = os.path.join(EXCEL_DIR, "users.xlsx")
        if os.path.exists(users_file):
            self.users_df = pd.read_excel(users_file)
        else:
            print("⚠️ Kullanıcı dosyası bulunamadı:", users_file)
            self.users_df = pd.DataFrame(columns=["username", "password", "role"])

        # Logo yükleme
        logo_path = os.path.join(IMG_DIR, "logo_butun.png")
        if os.path.exists(logo_path) and hasattr(self, "label"):
            self.label.setPixmap(QPixmap(logo_path))
            self.label.setScaledContents(True)

        # Buton bağlantıları
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
            role = match.iloc[0]['role']
            print(f"Giriş başarılı! Rol: {role}")

            if role == "admin":
                ui_path = os.path.join(UI_DIR, "Preference_Admin_Menu.ui")
            else:
                ui_path = os.path.join(UI_DIR, "Preference_Menu.ui")

            self.dashboard = PreferenceWindow(ui_path)
            self.dashboard.show()
            self.close()
        else:
            print("❌ Hatalı kullanıcı adı veya şifre.")


class PreferenceWindow(QMainWindow):
    def __init__(self, ui_path):
        super().__init__()
        loadUi(ui_path, self)
        self.setWindowTitle("CRM Preferences")
        self.setFixedSize(1000, 600)


def main():
    app = QApplication(sys.argv)
    splash = SplashScreen()
    splash.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
