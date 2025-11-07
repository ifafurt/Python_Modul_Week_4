import os
import pandas as pd
from PyQt6.uic import loadUi
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QTableWidgetItem, QHeaderView
from main import BaseWindow

BASE_DIR = os.path.dirname(__file__)
UI_DIR = os.path.join(BASE_DIR, "UI_s")
EXCEL_DIR = os.path.join(BASE_DIR, "Excels")

class MentorMeetingWindow(BaseWindow):
    def __init__(self, role="admin"):
        super().__init__()
        self.role = role
        loadUi(os.path.join(UI_DIR, "Mentor_Meeting_Page.ui"), self)
        self.setWindowTitle("Mentor Meeting Page")
        self.setFixedSize(1000, 600)
        self.move_to_last_position()
        
        header = self.tableWidget.horizontalHeader() 
        header.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        column_widths = [100, 200, 150, 120, 120, 200]  # tablo sütun sayısına göre ayarla
        for col, width in enumerate(column_widths):
            self.tableWidget.setColumnWidth(col, width)

        # Excel dosyasını yükle
        self.excel_file = os.path.join(EXCEL_DIR, "Mentor.xlsx")
        if os.path.exists(self.excel_file):
            df_full = pd.read_excel(self.excel_file, header=None)
            
            # İstenmeyen sütunları çıkar: 2., 6., 7.
            # Pandas sütunları 0-index, yani 2. = 1, 6. = 5, 7. = 6
            cols_to_use = [0, 2, 3, 4, 7, 5]  # 0=Interview Date, 2=Applicant Name, 3=Mentor Name, 4=IT Knowledge Level, 7=Workload Level, 5=Comments
            self.df = df_full.iloc[:, cols_to_use]
            self.df.columns = ["Interview Date", "Applicant Name", "Mentor Name",
                               "IT Knowledge Level", "Workload Level", "Comments"]
        else:
            self.df = pd.DataFrame(columns=["Interview Date", "Applicant Name", "Mentor Name",
                                            "IT Knowledge Level", "Workload Level", "Comments"])
            print("Mentor Excel file not found!")

        # Buton bağlantıları
        self.pushButton_Return_REFERENCE_menu.clicked.connect(self.return_to_menu)
        self.pushButton_EXIT.clicked.connect(self.close)
        self.pushButton_SEARCH.clicked.connect(self.search_action)
        self.lineEdit.textChanged.connect(self.search_action)  # CANLI ARAMA
        self.pushButton_ALL_MEETINGS.clicked.connect(self.show_all_records) 
        self.pushButton_ALL_MEETINGS.clicked.connect(self.clear_search_input)
        self.comboBox.currentTextChanged.connect(self.filter_by_comment)
        self.comboBox.currentTextChanged.connect(self.clear_search_input)

        # Tablonun başlıklarını ayarla
        self.tableWidget.setColumnCount(6)
        self.tableWidget.setHorizontalHeaderLabels(self.df.columns)

        # Tüm kayıtları göster başlangıçta
        self.show_all_records()
        
    def clear_search_input(self):
        self.lineEdit.clear()

    def return_to_menu(self):
        from main import PreferenceAdminMenu, PreferenceMenu
        if self.role.lower() == "admin":
            self.pref_menu = PreferenceAdminMenu(role=self.role)
        else:
            self.pref_menu = PreferenceMenu(role=self.role)
        self.pref_menu.show()
        self.close()
        
    def filter_by_comment(self, text):
        """ComboBox seçimine göre Comments sütununu filtrele."""
        try:
            if 'Comments' not in self.df.columns:
                print("'Comments' sütunu bulunamadı.")
                return

            if text == "" or text == "All":
                # Seçim yoksa tüm veriyi göster
                self.display_data(self.df)
                return

            filtered_df = self.df[self.df['Comments'] == text].reset_index(drop=True)
            self.display_data(filtered_df)
            print(f"ComboBox filtreleme: '{text}' seçildi, {len(filtered_df)} kayıt bulundu.")
        except Exception as e:
            print(f"filter_by_comment Hatası: {e}")

    def show_all_records(self):
        self.populate_table(self.df)
    
    def display_data(self, df):
        """DataFrame'i Mentor Meeting tablosuna yazdırır."""
        try:
            self.tableWidget.clearContents()
            self.tableWidget.setRowCount(0)

            if df is None or df.empty:
                print("Gösterilecek kayıt yok veya DataFrame boş.")
                return

            # Tablonun sütun sayısını ayarla
            self.tableWidget.setRowCount(len(df))
            self.tableWidget.setColumnCount(len(df.columns))
            self.tableWidget.setHorizontalHeaderLabels(df.columns.tolist())

            for row_idx, row in df.iterrows():
                for col_idx, value in enumerate(row):
                    item = QTableWidgetItem(str(value))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.tableWidget.setItem(row_idx, col_idx, item)

            print(f"{len(df)} kayıt tabloya yüklendi.\n")

        except Exception as e:
            print(f"display_data() Hatası: {e}")


    def search_action(self):
        """Search by Applicant or Mentor Name, display all if empty"""
        try:
            search_text = self.lineEdit.text().strip().lower()
            if not search_text:
                self.show_all_records()
                return

            df_clean = self.df.copy()
            df_clean['Applicant Name'] = df_clean['Applicant Name'].astype(str).str.lower().str.strip()
            df_clean['Mentor Name'] = df_clean['Mentor Name'].astype(str).str.lower().str.strip()

            mask = df_clean['Applicant Name'].apply(lambda x: search_text in x) | \
                df_clean['Mentor Name'].apply(lambda x: search_text in x)

            filtered_df = df_clean[mask].reset_index(drop=True)
            self.populate_table(filtered_df)
            

        except Exception as e:
            print(f"Search Error: {e}")


    def populate_table(self, df_to_show):
        self.tableWidget.setRowCount(len(df_to_show))
        for row_idx, row in df_to_show.iterrows():
            for col_idx, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                self.tableWidget.setItem(row_idx, col_idx, item)
        self.tableWidget.resizeColumnsToContents()


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = MentorMeetingWindow(role="admin")
    window.show()
    sys.exit(app.exec())
