
import os
import sys
import smtplib
from email.mime.text import MIMEText
import pandas as pd

from PyQt6.uic import loadUi
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QMessageBox,
    QTableWidgetItem
)

try:
    from main import BaseWindow
except Exception:
    from PyQt6.QtWidgets import QWidget as BaseWindow


BASE_DIR = os.path.dirname(__file__)
UI_DIR = os.path.join(BASE_DIR, "UI_s")
EXCEL_DIR = os.path.join(BASE_DIR, "Excels")  # Event.xlsx burada olacak


class AdminMenuWindow(BaseWindow):
    def __init__(self, role="admin"):
        super().__init__()

        ui_path = os.path.join(UI_DIR, "Admin_Menu.ui")

        try:
            loadUi(ui_path, self)
        except Exception as e:
            QMessageBox.critical(
                self, "UI Load Error",
                f"Failed to load UI:\n{ui_path}\n\n{e}"
            )
            raise

        self.role = role
        self.setWindowTitle("Admin Menu")
        self.setFixedSize(1000, 600)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)

        if hasattr(self, "move_to_last_position"):
            self.move_to_last_position()

        # --- Button connections ---
        self.pushButton_EVENT_REGISTRATION.clicked.connect(self.register_event)
        self.pushButton_SEND_EMAIL.clicked.connect(self.send_email)
        self.pushButton_Return_TO_ADMIN_PREFERENCE_menu.clicked.connect(self.return_to_admin_pref_menu)
        self.pushButton_Exit.clicked.connect(self.close)

        self.tableWidget.setColumnCount(4)


   
    # 1) Excel (Event.xlsx) → Tabloya yükleme
    
    def register_event(self):
        excel_path = os.path.join(EXCEL_DIR, "Event.xlsx")

        if not os.path.exists(excel_path):
            QMessageBox.warning(self, "Missing File", f"Event.xlsx not found:\n{excel_path}")
            return

        try:
            df = pd.read_excel(excel_path)

            required_columns = [
                "EVENT NAME",
                "START TIME",
                "PARTICIPANT E-MAIL",
                "ORGANIZER E-MAIL"
            ]

            for col in required_columns:
                if col not in df.columns:
                    QMessageBox.critical(
                        self,
                        "Column Error",
                        f"Missing column in Event.xlsx:\n'{col}'"
                    )
                    return

            self.tableWidget.setRowCount(0)

            for row_idx, row in df.iterrows():
                self.tableWidget.insertRow(row_idx)
                self.tableWidget.setItem(row_idx, 0, QTableWidgetItem(str(row["EVENT NAME"])))
                self.tableWidget.setItem(row_idx, 1, QTableWidgetItem(str(row["START TIME"])))
                self.tableWidget.setItem(row_idx, 2, QTableWidgetItem(str(row["PARTICIPANT E-MAIL"])))
                self.tableWidget.setItem(row_idx, 3, QTableWidgetItem(str(row["ORGANIZER E-MAIL"])))

        except Exception as e:
            QMessageBox.critical(self, "Excel Error", f"Failed to read Event.xlsx:\n{e}")


    # 2-Gerçek Mail Gönderme (Gmail App Password gerekli)
  
    def send_email(self):
        rows = self.tableWidget.rowCount()

        if rows == 0:
            QMessageBox.warning(self, "No Data", "No events loaded.")
            return

        SMTP_SERVER = "smtp.gmail.com"
        SMTP_PORT = 587

        #  BURAYI KENDİ GMAIL HESABINLA DOLDURACAKSIN
        SENDER_EMAIL = "your_email@gmail.com"
        SENDER_PASSWORD = "your_app_password"  # Gmail App Password

        if "your_email" in SENDER_EMAIL:
            QMessageBox.warning(
                self,
                "Setup Needed",
                "Please set your Gmail address and App Password in the code."
            )
            return

        try:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=20)
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)

            sent_count = 0

            for r in range(rows):
                event_name = self._safe(r, 0)
                participant = self._safe(r, 2)
                organizer = self._safe(r, 3)

                emails = self._split_emails(participant) + self._split_emails(organizer)

                if not emails:
                    continue

                msg = MIMEText(
                    f"Hello,\n\nThis is a reminder for the event:\n\n"
                    f"{event_name}\n\nBest regards,\nCRM System"
                )
                msg["Subject"] = f"Event Reminder – {event_name}"
                msg["From"] = SENDER_EMAIL

                for email in emails:
                    msg["To"] = email
                    server.sendmail(SENDER_EMAIL, email, msg.as_string())
                    sent_count += 1

            server.quit()

            QMessageBox.information(self, "Success", f"Emails sent: {sent_count}")

        except smtplib.SMTPAuthenticationError:
            QMessageBox.critical(
                self,
                "Authentication Error",
                "Gmail blocked the login.\n"
                "You MUST use a Gmail App Password:\n"
                "Google Account → Security → App Passwords."
            )
        except Exception as e:
            QMessageBox.critical(self, "Email Error", str(e))


    def _safe(self, r, c):
        item = self.tableWidget.item(r, c)
        return item.text().strip() if item else ""

    def _split_emails(self, text):
        if not text:
            return []
        parts = [p.strip() for p in text.replace(";", ",").split(",")]
        return [p for p in parts if "@" in p]


    # RETURN — Admin Preference Menu’ye geri dön
    def return_to_admin_pref_menu(self):
    # 1) Normal durumda: proje main.py'den çalışınca
        try:
            from main import PreferenceAdminMenu
        except ImportError:
        # 2) Python main.py'yi __main__ olarak çalıştırdıysa burası devreye girer
            try:
                from __main__ import PreferenceAdminMenu
            except ImportError:
                QMessageBox.warning(
                    self,
                    "Return Error",
                    "Cannot return to previous menu because main module was not found."
            )
            return
        self.new_window = PreferenceAdminMenu(role=self.role)  # REFERANS ÖNEMLİ
        self.new_window.show()
        self.close()
   



if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = AdminMenuWindow()
    w.show()
    sys.exit(app.exec())



