import cv2
import sys
from PyQt6.QtWidgets import QApplication, QPushButton, QLabel, QVBoxLayout, QWidget
from PyQt6.QtCore import QSize, Qt, QTimer
from PyQt6.QtGui import QImage, QIcon, QPixmap

class Camera_App(QWidget): #Inherits basic GUI window
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mini Camera App")
        self.setStyleSheet("background-color: #1e1e1e; color: white")
        self.setFixedSize(1280,720)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Camera_App()
    window.show()
    sys.exit(app.exec())



