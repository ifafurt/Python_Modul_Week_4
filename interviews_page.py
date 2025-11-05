
import os
import pandas as pd
from PyQt6.uic import loadUi
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMessageBox, QTableWidgetItem, QApplication
from main import BaseWindow

BASE_DIR = os.path.dirname(__file__)
UI_DIR = os.path.join(BASE_DIR, "UI_s")
EXCEL_PATH = os.path.join(BASE_DIR, "Excels", "Interviews.xlsx")


class InterviewsWindow(BaseWindow):
    def __init__(self, role="admin"):
        super().__init__()
        self.role = role
        loadUi(os.path.join(UI_DIR, "Interviews.ui"), self)
        self.setWindowTitle("Interviews")
        self.setFixedSize(1000, 600)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.move_to_last_position()

        # Excel yükleme ve normalize edilmiş kolon isimleri
        if os.path.exists(EXCEL_PATH):
            try:
                self.df = pd.read_excel(EXCEL_PATH)
            except Exception as e:
                QMessageBox.critical(self, "Dosya Hatası", f"Excel okunamadı:\n{e}")
                self.df = pd.DataFrame()
        else:
            QMessageBox.critical(self, "Dosya Hatası", f"Excel dosyası bulunamadı:\n{EXCEL_PATH}")
            self.df = pd.DataFrame()

        # Normalize: ayrıca indekslenmiş küçük harfli isimlere erişim için bir yardımcı dict oluştur
        # (orijinal sütun adlarını koruyoruz ancak lowercase anahtarlarla arama yapacağız)
        self.col_map = {}
        if not self.df.empty:
            for c in self.df.columns:
                self.col_map[c.strip().lower()] = c  # map: lowercase -> gerçek sütun adı

        # Olası sütun isimlerini tespit et (Türkçe ve İngilizce olasılıkları)
        self.name_col = self._pick_column(["full name", "adınız soyadınız", "adınız soyadınız", "ad soyad", "adiniz soyadiniz"])
        self.submitted_col = self._pick_column(["submitted project", "proje gonderilis tarihi", "proje gönderiliş tarihi", "project submitted", "submitted"])
        self.received_col = self._pick_column(["received project", "projenin gelis tarihi", "proje gelis tarihi", "received"])

        # Bağlantılar
        self.pushButton_Return_REFERENCE_menu.clicked.connect(self.return_to_menu)
        self.pushButton_EXIT.clicked.connect(self.close)
        self.pushButton_SEARCH.clicked.connect(self.search_action)
        self.pushButton_SUBMITTED_PROJECTS.clicked.connect(self.show_submitted_projects)
        self.pushButton_RECEIVED_PROJECTS.clicked.connect(self.show_received_projects)

        # Tablo başlıkları (UI'da Türkçe görünmesini istersen burayı bırak)
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setHorizontalHeaderLabels([
            "Adı Soyadı", "Proje Gönderiliş Tarihi", "Proje Geliş Tarihi"
        ])
        

    def _pick_column(self, candidates):
        """Verilen anahtar listesine göre ilk eşleşen gerçek sütun adını döndürür."""
        if self.df.empty:
            return None
        lower_cols = [c.lower().strip() for c in self.df.columns]
        for cand in candidates:
            cand_low = cand.lower().strip()
            for i, lc in enumerate(lower_cols):
                # Tam veya içinde eşleşme kabul edelim
                if cand_low == lc or cand_low in lc or lc in cand_low:
                    return self.df.columns[i]
        return None

    def fill_table(self, data: pd.DataFrame):
        """Tabloyu verilen DataFrame'e göre doldurur (görsel Türkçe başlıklar)."""
        self.tableWidget.setRowCount(0)
        for row_idx, row in data.reset_index(drop=True).iterrows():
            self.tableWidget.insertRow(row_idx)
            # Eğer sütun yoksa boş string koy
            name_val = row.get(self.name_col, "") if self.name_col in row.index else row.get("Adınız Soyadınız", "")
            sub_val = row.get(self.submitted_col, "") if self.submitted_col in row.index else row.get("Proje gonderilis tarihi", "")
            rec_val = row.get(self.received_col, "") if self.received_col in row.index else row.get("Projenin gelis tarihi", "")

            self.tableWidget.setItem(row_idx, 0, QTableWidgetItem("" if pd.isna(name_val) else str(name_val)))
            self.tableWidget.setItem(row_idx, 1, QTableWidgetItem("" if pd.isna(sub_val) else str(sub_val)))
            self.tableWidget.setItem(row_idx, 2, QTableWidgetItem("" if pd.isna(rec_val) else str(rec_val)))
        self.tableWidget.resizeColumnsToContents()

    def search_action(self):
        """NAME sütununda BAŞLANGIÇ (startswith) araması yapar, case-insensitive."""
        if self.name_col is None:
            QMessageBox.critical(self, "Hata", "Ad/Soyad sütunu bulunamadı (Excel).")
            return
        text = self.lineEdit.text().strip()
        if text == "":
            QMessageBox.information(self, "Bilgi", "Lütfen arama kutusuna bir metin girin.")
            return

        # Case-insensitive, baştan eşleşme. NaN güvenli.
        series = self.df[self.name_col].astype(str).str.strip()
        mask = series.str.lower().str.startswith(text.lower(), na=False)
        filtered = self.df[mask]
        if filtered.empty:
            QMessageBox.information(self, "Sonuç Yok", f"'{text}' ile başlayan isim bulunamadı.")
            # istersen tümünü gösterme, şu an sadece uyarı
        else:
            self.fill_table(filtered)


    def show_submitted_projects(self):
    # """Projesini göndermiş adayları göster."""
    # Sütun adlarını normalize et (boşlukları ve büyük harfleri temizle)
        self.df.columns = [col.strip().upper() for col in self.df.columns]

        if "SUBMITTED PROJECT" not in self.df.columns:
            QMessageBox.critical(self, "Hata", "'SUBMITTED PROJECT' sütunu Excel dosyasında bulunamadı.")
            return

    # Boş olmayan satırları filtrele
        submitted = self.df[self.df["SUBMITTED PROJECT"].notna() & (self.df["SUBMITTED PROJECT"].astype(str).str.strip() != "")]

        if submitted.empty:
            QMessageBox.information(self, "Bilgi", "Proje göndermiş aday bulunamadı.")
        else:
            self.fill_table(submitted)



    def show_received_projects(self):
    # """Projesi GELMİŞ adayları göster."""
        if self.received_col is None:
            QMessageBox.critical(self, "Hata", "Received (geliş) sütunu bulunamadı.")
            return

        r = self.df[self.received_col]
        mask = r.notna() & (r.astype(str).str.strip() != "")
        res = self.df[mask]
        if res.empty:
            QMessageBox.information(self, "Bilgi", "Projesi gelmiş aday bulunamadı.")
        else:
            self.fill_table(res)

    
    

    def return_to_menu(self):
        from main import PreferenceAdminMenu, PreferenceMenu
        if self.role.lower() == "admin":
            self.pref_menu = PreferenceAdminMenu(role=self.role)
        else:
            self.pref_menu = PreferenceMenu(role=self.role)
        self.pref_menu.show()
        self.close()


# standalone test
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    w = InterviewsWindow(role="admin")
    w.show()
    sys.exit(app.exec())

