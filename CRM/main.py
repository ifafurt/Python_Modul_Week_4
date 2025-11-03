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
