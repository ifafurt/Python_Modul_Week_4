import sys
import os
import pandas as pd
from PyQt6.QtWidgets import QApplication, QHeaderView, QTableWidgetItem
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

        # Excel başlıkları ve UI başlıkları artık aynı
        self.table_columns = [
            "DATE",
            "FULL NAME",
            "E-MAIL",
            "PHONE NUMBER",
            "POSTAL CODE",
            "PROVINCE",
            "CURRENT STATUS"
        ]

        self.setWindowTitle("Applications")
        self.setFixedSize(1000, 600)
        self.move_to_last_position()
       
        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        column_widths = [100, 200, 150, 120, 120, 200]  # tablo sütun sayısına göre ayarla
        for col, width in enumerate(column_widths):
            self.tableWidget.setColumnWidth(col, width)

        # Excel dosyalarını yükle
        self.applications_file = os.path.join(EXCEL_DIR, "Basvurular.xlsx")
        self.vit1_file = os.path.join(EXCEL_DIR, "VIT1.xlsx")
        self.vit2_file = os.path.join(EXCEL_DIR, "VIT2.xlsx")

        self.df = pd.read_excel(self.applications_file) if os.path.exists(self.applications_file) else pd.DataFrame()
        self.vit1_df = pd.read_excel(self.vit1_file) if os.path.exists(self.vit1_file) else pd.DataFrame()
        self.vit2_df = pd.read_excel(self.vit2_file) if os.path.exists(self.vit2_file) else pd.DataFrame()

        # Butonlara fonksiyon bağla
        self.pushButton_SEARCH.clicked.connect(self.search_applications)
        self.lineEdit.textChanged.connect(self.search_applications)  # CANLI ARAMA
        self.pushButton_ALL_APPLICATIONS.clicked.connect(self.load_all_applications)
        self.pushButton_ALL_APPLICATIONS.clicked.connect(self.clear_search_input)
        self.pushButton_DEFINED_MENTOR_MEETING.clicked.connect(self.show_defined_mentor)
        self.pushButton_DEFINED_MENTOR_MEETING.clicked.connect(self.clear_search_input)
        self.pushButton_UNDEFINED_MENTOR_MEETING.clicked.connect(self.show_undefined_mentor)
        self.pushButton_UNDEFINED_MENTOR_MEETING.clicked.connect(self.clear_search_input)
        self.pushButton_DUPLICATE_REGISTRATION.clicked.connect(self.show_duplicates)
        self.pushButton_DUPLICATE_REGISTRATION.clicked.connect(self.clear_search_input)
        self.pushButton_PREVIOUS_VIT_CHECK.clicked.connect(self.show_previous_vit)
        self.pushButton_PREVIOUS_VIT_CHECK.clicked.connect(self.clear_search_input)
        self.pushButton_DIFFERENT_REGISTRATION.clicked.connect(self.show_different)
        self.pushButton_DIFFERENT_REGISTRATION.clicked.connect(self.clear_search_input)
        self.pushButton_APPLICATION_FILTERING.clicked.connect(self.filter_applications)
        self.pushButton_APPLICATION_FILTERING.clicked.connect(self.clear_search_input)
        self.pushButton_RETURN_REFERENCE_MENU.clicked.connect(self.return_to_menu)

    # ---------------- Fonksiyonlar ---------------- #
    def clear_search_input(self):
        self.lineEdit.clear()    #Herhangi bir butona basildiginda onceki yapilan arama silinsin

    def display_data(self, df):
        """DataFrame'i tabloya yazdır — artık UI başlıkları Excel başlıkları ile aynı."""
        try:
            self.tableWidget.clearContents()
            self.tableWidget.setRowCount(0)

            if df is None or df.empty:
                print("Gösterilecek kayıt yok veya DataFrame boş.")
                return

            display_df = df.copy()
            for col in self.table_columns:
                if col not in display_df.columns:
                    display_df[col] = ""
            display_df = display_df.reset_index(drop=True)

            self.tableWidget.setRowCount(len(display_df))
            self.tableWidget.setColumnCount(len(self.table_columns))
            self.tableWidget.setHorizontalHeaderLabels(self.table_columns)

            for row_idx, row in display_df.iterrows():
                for col_idx, col_name in enumerate(self.table_columns):
                    value = row[col_name] if col_name in row else ""
                    item = QTableWidgetItem(str(value))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.tableWidget.setItem(row_idx, col_idx, item)

            print(f"{len(display_df)} kayıt tabloya yüklendi.\n")

        except Exception as e:
            print(f"display_data() Hatası: {e}")

    def search_applications(self):
        """LineEdit içindeki metin ile FULL NAME araması."""
        try:
            search_text = self.lineEdit.text().strip().lower()
            print("Arama metni:", search_text)

            if 'FULL NAME' not in self.df.columns:
                print("'FULL NAME' sütunu bulunamadı.")
                return

            if not search_text:
                self.display_data(self.df)
                return

            df_clean = self.df.copy()
            df_clean['FULL NAME'] = df_clean['FULL NAME'].astype(str).str.lower().str.strip()
            mask = df_clean['FULL NAME'].apply(lambda x: search_text in x)
            filtered_df = df_clean[mask].reset_index(drop=True)

            print("Arama sonucu:", filtered_df[['FULL NAME']].to_string(index=False))
            self.display_data(filtered_df)
            

        except Exception as e:
            print(f"Search Error: {e}")

    def load_all_applications(self):
        print(f"Toplam kayıt sayısı: {len(self.df)}")
        self.display_data(self.df)
        print("Tüm başvurular görüntülendi.\n")

    def show_defined_mentor(self):
        if 'MENTOR MEETING' in self.df.columns:
            filtered_df = self.df[self.df['MENTOR MEETING'] == 'OK']
            print(f"Mentoru atanmış adaylar filtrelendi: {len(filtered_df)} kayıt bulundu.")
            self.display_data(filtered_df)

    def show_undefined_mentor(self):
        if 'MENTOR MEETING' in self.df.columns:
            filtered_df = self.df[self.df['MENTOR MEETING'] == 'ATANMADI']
            print(f"Mentoru atanmamış adaylar filtrelendi: {len(filtered_df)} kayıt bulundu.")
            self.display_data(filtered_df)

    def show_duplicates(self):
        if all(col in self.df.columns for col in ['FULL NAME', 'E-MAIL']):
            duplicates = self.df[self.df.duplicated(subset=['FULL NAME', 'E-MAIL'], keep=False)]
            print(f"Mükerrer kayıtlar bulundu: {len(duplicates)}")
            self.display_data(duplicates)

    def filter_applications(self):
        """Tekil kayıtları göster (FULL NAME + E-MAIL)."""
        if all(col in self.df.columns for col in ['FULL NAME', 'E-MAIL']):
            filtered = self.df.drop_duplicates(subset=['FULL NAME', 'E-MAIL'], keep='first')
            self.display_data(filtered)
            print("Tekil kayıtlar başarıyla listelendi.\n")

    def show_previous_vit(self):
        """VIT1 veya VIT2 ile ortak adayları göster."""
        if self.vit1_df.empty and self.vit2_df.empty:
            print("VIT1 ve VIT2 dosyaları bulunamadı.")
            self.tableWidget.setRowCount(0)
            return

        vit_all = pd.concat([self.vit1_df, self.vit2_df], ignore_index=True)

        # Sadece FULL NAME ve E-MAIL ile merge yap, orijinal df’den diğer sütunları al
        common_keys = ['FULL NAME', 'E-MAIL']
        merged = self.df.merge(vit_all[common_keys], how='inner', on=common_keys)
        print(f"VIT1/VIT2 ile ortak kayıtlar bulundu: {len(merged)}")
        self.display_data(merged)


    def show_different(self):
        """VIT1 ve VIT2’de olmayan adayları göster."""
        if self.vit1_df.empty and self.vit2_df.empty:
            print("VIT1 ve VIT2 dosyaları bulunamadı.")
            self.tableWidget.setRowCount(0)
            return

        vit_all = pd.concat([self.vit1_df, self.vit2_df], ignore_index=True)
        keys = ['FULL NAME', 'E-MAIL']
        different_keys = self.df.merge(vit_all[keys], how='left', on=keys, indicator=True)
        different = self.df[different_keys['_merge'] == 'left_only']
        print(f"VIT1/VIT2’de olmayan adaylar: {len(different)}")
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
