import os
import pandas as pd
from PyQt6.uic import loadUi
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QTableWidgetItem
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

        # Excel dosyasını yükle
        self.excel_file = os.path.join(EXCEL_DIR, "Mentor.xlsx")
        if os.path.exists(self.excel_file):
            df_full = pd.read_excel(self.excel_file, header=None)
            
            # İstenmeyen sütunları çıkar:
            # Pandas sütunları 0-index, yani 2. = 1, 6. = 5, 7. = 6
            cols_to_use = [0, 2, 3, 4, 7, 8]  # 0=Interview Date, 2=Applicant Name, 3=Mentor Name, 4=IT Knowledge Level, 7=Workload Level, 8=Comments
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
        self.pushButton_ALL_MEETINGS.clicked.connect(self.show_all_records)  # "All Records" butonu

        # Tablonun başlıklarını ayarla
        self.tableWidget.setColumnCount(6)
        self.tableWidget.setHorizontalHeaderLabels(self.df.columns)

        # Tüm kayıtları göster başlangıçta
        self.show_all_records()

    def return_to_menu(self):
        from main import PreferenceAdminMenu, PreferenceMenu
        if self.role.lower() == "admin":
            self.pref_menu = PreferenceAdminMenu(role=self.role)
        else:
            self.pref_menu = PreferenceMenu(role=self.role)
        self.pref_menu.show()
        self.close()

    def show_all_records(self):
        self.populate_table(self.df)

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
