
#admin_menu_page.py 

import os
import sys
import smtplib
from email.mime.text import MIMEText

from PyQt6.uic import loadUi
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QMessageBox,
    QTableWidgetItem,
)

# ---- BaseWindow: main.py'den geliyorsa kullan, yoksa QWidget'e düş ----
try:
    from main import BaseWindow  # proje içinden çalışırken
except Exception:
    from PyQt6.QtWidgets import QWidget as BaseWindow  # tek başına koşarken

# ---- ODS okuma için odfpy ----
from odf.opendocument import load as odf_load
from odf.table import Table, TableRow, TableCell
from odf.text import P


BASE_DIR = os.path.dirname(__file__)
UI_DIR = os.path.join(BASE_DIR, "UI_s")
EXCEL_DIR = os.path.join(BASE_DIR, "Excels")  # Event.ods burada olmalı


class AdminMenuWindow(BaseWindow):
    def __init__(self, role: str = "admin"):
        super().__init__()
        ui_path = os.path.join(UI_DIR, "Admin_Menu.ui")

        # UI yükle (sessiz çökme yaşanmaması için try/except)
        try:
            loadUi(ui_path, self)
        except Exception as e:
            QMessageBox.critical(
                self, "UI Load Error",
                f"Failed to load UI file:\n{ui_path}\n\n{e}"
            )
            raise

        self.role = role
        self.setWindowTitle("Admin Menu")
        self.setFixedSize(1000, 600)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        # BaseWindow varsa pencere konumunu korur
        if hasattr(self, "move_to_last_position"):
            self.move_to_last_position()

        # --- Buttons ---
        self.pushButton_EVENT_REGISTRATION.clicked.connect(self.register_event)
        self.pushButton_SEND_EMAIL.clicked.connect(self.send_email)
        self.pushButton_Return_TO_ADMIN_PREFERENCE_menu.clicked.connect(self.return_to_admin_pref_menu)
        self.pushButton_Exit.clicked.connect(self.close)

        # --- Table hardening ---
        # Kolon sayısı UI'da 4; başlıklar UI içinde zaten yazılı
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setSortingEnabled(False)

    # =========================
    # 1) ODS → tabloya yükle
    # =========================
    def register_event(self):
        """
        Excels/Event.ods içindeki ilk çalışma sayfasını okur ve tabloya basar.
        Sütun beklenen sıra:
            0: Event Name
            1: Start Time
            2: Participant Email
            3: Organizer Email
        """
        ods_path = os.path.join(EXCEL_DIR, "Event.ods")
        if not os.path.exists(ods_path):
            QMessageBox.warning(self, "Missing File", f"Event.ods not found:\n{ods_path}")
            return

        try:
            doc = odf_load(ods_path)
            table = doc.spreadsheet.getElementsByType(Table)[0]

            rows = []
            for row in table.getElementsByType(TableRow):
                vals = []
                for cell in row.getElementsByType(TableCell):
                    # ODS hücresindeki tüm <text:p> satırlarını birleştir
                    txt_parts = [str(p) for p in cell.getElementsByType(P)]
                    vals.append(" ".join(txt_parts).strip())
                # Satırda tamamen boş olmayan bir değer varsa ekle
                if any(v.strip() for v in vals):
                    rows.append(vals)

            # İlk satır başlık ise at (başlık kontrolü gevşek)
            if rows and self._looks_like_header(rows[0]):
                rows = rows[1:]

            # Tabloya yaz
            self.tableWidget.clearContents()
            self.tableWidget.setRowCount(len(rows))
            for r, row_vals in enumerate(rows):
                for c in range(4):
                    text = row_vals[c] if c < len(row_vals) else ""
                    item = QTableWidgetItem(text)
                    item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                    self.tableWidget.setItem(r, c, item)

            # İstenirse başarı popup’ı gösterilebilir; sunum için sessiz bırakıyoruz.
            # QMessageBox.information(self, "Success", "Events loaded successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Read Error", f"Failed to read ODS:\n{e}")

    def _looks_like_header(self, first_row):
        header_tokens = ["event", "name", "start", "time", "email", "participant", "organizer"]
        joined = " ".join(first_row).lower()
        return any(tok in joined for tok in header_tokens)

    # =========================
    # 2) Gerçek e-posta gönder
    # =========================
    def send_email(self):
        """
        Tablo satırlarını dolaşır; 2. ve 3. sütundaki adreslere
        etkinlik adına göre basit bir bilgilendirme maili yollar.
        Gmail ile çalışır: 2-Adımlı Doğrulama açık + App Password gerekli.
        """
        rows = self.tableWidget.rowCount()
        if rows == 0:
            QMessageBox.warning(self, "No Data", "No events loaded.")
            return

        # ---- SMTP ayarlarını BURAYA koy ----
        SMTP_SERVER = "smtp.gmail.com"
        SMTP_PORT = 587
        SENDER_EMAIL = "your_email@gmail.com"       # <-- kendi adresin
        SENDER_PASSWORD = "your_app_password"       # <-- Gmail App Password

        # Basit doğrulama
        if "your_email" in SENDER_EMAIL or "your_app_password" in SENDER_PASSWORD:
            QMessageBox.warning(
                self, "Setup Required",
                "Please set SENDER_EMAIL and SENDER_PASSWORD (Gmail App Password)."
            )
            return

        try:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=20)
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)

            total_sent = 0

            for r in range(rows):
                event_name = self._safe_item_text(r, 0)
                participant = self._safe_item_text(r, 2)
                organizer = self._safe_item_text(r, 3)

                # adresleri virgül/ noktalı virgül ile ayırmayı destekle
                targets = []
                targets += self._split_emails(participant)
                targets += self._split_emails(organizer)

                if not targets:
                    continue

                msg = MIMEText(
                    f"Hello,\n\nThis is a reminder for the event:\n\n"
                    f"  {event_name}\n\n"
                    f"Best regards,\nCRM Bot"
                )
                msg["Subject"] = f"Event Reminder – {event_name}"
                msg["From"] = SENDER_EMAIL

                for to_addr in targets:
                    msg["To"] = to_addr
                    server.sendmail(SENDER_EMAIL, to_addr, msg.as_string())
                    total_sent += 1

            server.quit()
            QMessageBox.information(self, "Emails Sent", f"Successfully sent {total_sent} email(s).")

        except smtplib.SMTPAuthenticationError as e:
            QMessageBox.critical(
                self, "Auth Error",
                "SMTP authentication failed.\n\n"
                "Gmail için:\n"
                "1) Google hesabında 2-Adımlı Doğrulama açık olmalı\n"
                "2) App Password oluşturup SENDER_PASSWORD olarak kullanmalısın.\n\n"
                f"Details:\n{e}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Email Error", f"Failed to send emails:\n{e}")

    def _safe_item_text(self, row: int, col: int) -> str:
        it = self.tableWidget.item(row, col)
        return it.text().strip() if it else ""

    def _split_emails(self, raw: str) -> list[str]:
        if not raw:
            return []
        # virgül veya noktalı virgül ile ayır
        parts = [p.strip() for p in raw.replace(";", ",").split(",")]
        # boşları ayıkla, çok basit bir '@' kontrolü
        return [p for p in parts if p and "@" in p]
    
    def return_to_admin_pref_menu(self):
        from main import PreferenceAdminMenu
        self.pref_menu = PreferenceAdminMenu(role=self.role)
        self.pref_menu.show()
        self.close()
    

# ---- Tek başına çalıştırma (runner) ----
if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = AdminMenuWindow()
    w.show()
    sys.exit(app.exec())
