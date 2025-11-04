import sys
import os
import pandas as pd
from PyQt6.QtWidgets import QApplication, QWidget, QTableWidgetItem
from PyQt6.uic import loadUi
from PyQt6.QtCore import Qt
from main import BaseWindow

# Klasör yolları
BASE_DIR = os.path.dirname(__file__)
UI_DIR = os.path.join(BASE_DIR, "UI_s")
EXCEL_DIR = os.path.join(BASE_DIR, "Excels")

class ApplicationsWindow(BaseWindow):
    def __init__(self, role="admin"):
        super().__init__()
        self.role = role
        loadUi(os.path.join(UI_DIR, "Applications.ui"), self)
        self.setWindowTitle("Applications")
        self.setFixedSize(1000, 600)
        self.move_to_last_position()

        # Excel dosyalarını yükle
        self.applications_file = os.path.join(EXCEL_DIR, "Basvurular.xlsx")
        self.vit1_file = os.path.join(EXCEL_DIR, "VIT1.xlsx")
        self.vit2_file = os.path.join(EXCEL_DIR, "VIT2.xlsx")

        self.df = pd.read_excel(self.applications_file) if os.path.exists(self.applications_file) else pd.DataFrame()
        self.vit1_df = pd.read_excel(self.vit1_file) if os.path.exists(self.vit1_file) else pd.DataFrame()
        self.vit2_df = pd.read_excel(self.vit2_file) if os.path.exists(self.vit2_file) else pd.DataFrame()

        # Butonlara fonksiyon bağla
        self.pushButton_SEARCH.clicked.connect(self.search_applications)
        self.pushButton_ALL_APPLICATIONS.clicked.connect(self.load_all_applications)
        self.pushButton_DEFINED_MENTOR_MEETING.clicked.connect(self.show_defined_mentor)
        self.pushButton_UNDEFINED_MENTOR_MEETING.clicked.connect(self.show_undefined_mentor)
        self.pushButton_DUPLICATE_REGISTRATION.clicked.connect(self.show_duplicates)
        self.pushButton_PREVIOUS_VIT_CHECK.clicked.connect(self.show_previous_vit)
        self.pushButton_DIFFERENT_REGISTRATION.clicked.connect(self.show_different)
        self.pushButton_APPLICATION_FILTERING.clicked.connect(self.filter_applications)
        self.pushButton_RETURN_REFERENCE_MENU.clicked.connect(self.return_to_menu)

    # ---------------- Fonksiyonlar ---------------- #

    def display_data(self, df):
        """DataFrame'i tabloya yazdır."""
        self.tableWidget.clearContents()  # önceki içerikleri temizle
        self.tableWidget.setRowCount(0)   # satır sayısını sıfırla
        if df.empty:
            print("Gösterilecek kayıt yok.")
            return
        df = df.reset_index(drop=True)  # ← indeksleri sıfırla
        self.tableWidget.setRowCount(len(df))
        self.tableWidget.setColumnCount(len(df.columns))
        self.tableWidget.setHorizontalHeaderLabels(df.columns)
        for row_idx, row in df.iterrows():
            for col_idx, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tableWidget.setItem(row_idx, col_idx, item)

    
    def search_applications(self):
        """Arama fonksiyonu: lineEdit içindeki metin ile isim/soyisim araması."""
        try:
            search_text = self.lineEdit.text().strip().lower()
            print("Arama metni:", search_text)

            if 'Adınız Soyadınız' not in self.df.columns:
                print("'Adınız Soyadınız' sütunu bulunamadı.")
                return

            if not search_text:
                self.display_data(self.df)
                return

            # Veriyi temizle
            df_clean = self.df.copy()
            df_clean['Adınız Soyadınız'] = df_clean['Adınız Soyadınız'].astype(str).str.lower().str.strip()

            # Arama mantığı: içinde geçiyorsa eşleştir
            mask = df_clean['Adınız Soyadınız'].apply(lambda x: search_text in x)
            filtered_df = df_clean[mask].reset_index(drop=True)

            print("Arama sonucu:", filtered_df[['Adınız Soyadınız']].to_string(index=False))

            self.display_data(filtered_df)
        except Exception as e:
            print(f"Search Error: {e}")


    def load_all_applications(self):
        """Tüm başvuruları tabloya yazdır."""
        self.display_data(self.df)

    def show_defined_mentor(self):
        if 'Mentor gorusmesi' in self.df.columns:
            filtered_df = self.df[self.df['Mentor gorusmesi'] == 'OK']
            print(f"Mentoru atanmış adaylar: {len(filtered_df)} kayıt bulundu.")
            self.display_data(filtered_df)

    def show_undefined_mentor(self):
        if 'Mentor gorusmesi' in self.df.columns:
            filtered_df = self.df[self.df['Mentor gorusmesi'] == 'ATANMADI']
            print(f"Mentoru atanmamış adaylar: {len(filtered_df)} kayıt bulundu.")
            self.display_data(filtered_df)


    def show_duplicates(self):
        """Aynı isim ve e-posta ile kayıtlı adayları göster."""
        if all(col in self.df.columns for col in ['Adınız Soyadınız', 'Mail adresiniz']):
            duplicates = self.df[self.df.duplicated(subset=['Adınız Soyadınız', 'Mail adresiniz'], keep=False)]
            self.display_data(duplicates)

    def filter_applications(self):
        """Duplicate kayıtları filtrele ve sadece tekil göster."""
        if all(col in self.df.columns for col in ['Adınız Soyadınız', 'Mail adresiniz']):
            filtered = self.df.drop_duplicates(subset=['Adınız Soyadınız', 'Mail adresiniz'])
            self.display_data(filtered)

    def show_previous_vit(self):
        """VIT1 veya VIT2 ile ortak adayları göster."""
        if self.vit1_df.empty and self.vit2_df.empty:
            print("VIT1 ve VIT2 dosyaları bulunamadı.")
            self.tableWidget.setRowCount(0)
            return
        vit_all = pd.concat([self.vit1_df, self.vit2_df], ignore_index=True)
        common = self.df.merge(vit_all, how='inner', on=['Adınız Soyadınız', 'Mail adresiniz'])
        self.display_data(common)

    def show_different(self):
        """VIT1 ve VIT2’de olmayan adayları göster."""
        if self.vit1_df.empty and self.vit2_df.empty:
            print("VIT1 ve VIT2 dosyaları bulunamadı.")
            self.tableWidget.setRowCount(0)
            return
        vit_all = pd.concat([self.vit1_df, self.vit2_df], ignore_index=True)
        different = self.df.merge(vit_all, how='left', on=['Adınız Soyadınız', 'Mail adresiniz'], indicator=True)
        different = different[different['_merge'] == 'left_only'].drop(columns=['_merge'])
        self.display_data(different)

    def return_to_menu(self):
        from main import PreferenceAdminMenu, PreferenceMenu
        if self.role.lower() == "admin":
            self.pref_menu = PreferenceAdminMenu(role=self.role)
        else:
            self.pref_menu = PreferenceMenu(role=self.role)
        self.pref_menu.show()
        self.close()


# ----------------- Main ----------------- #
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ApplicationsWindow(role="admin")
    window.show()
    sys.exit(app.exec())
