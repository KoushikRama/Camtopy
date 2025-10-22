import cv2
import sys
from PyQt6.QtWidgets import QApplication, QPushButton, QLabel,QHBoxLayout, QVBoxLayout, QWidget
from PyQt6.QtCore import QSize, Qt, QTimer
from PyQt6.QtGui import QImage, QIcon, QPixmap

class Camera_App(QWidget): #Inherits basic GUI window
    def __init__(self):
        super().__init__()
        #window setting
        self.setWindowTitle("Mini Camera App")
        self.setStyleSheet("background-color: #1e1e1e; color: white")
        self.setFixedSize(1280,720)
        
        #Camera setting
        self.cam = cv2.VideoCapture(0)
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        #Webcam view setting
        self.videoLabel = QLabel()
        self.videoLabel.setFixedSize(960,720)

        #Buttons setting
        #Photo button
        self.photo_btn = QPushButton()
        self.photo_btn.setIcon(QIcon("pictures/Picture.png"))
        self.photo_btn.setIconSize(QSize(60,60))
        self.photo_btn.setFixedSize(80,80)
        self.photo_btn.setStyleSheet("border-radius: 40px; border:none; background-color: #2e2e2e;") 
        #self.photo_btn.clicked.connect(self.capture_photo)

        #Video button
        self.video_btn = QPushButton()
        self.video_btn.setIcon(QIcon("pictures/Video.png"))
        self.video_btn.setIconSize(QSize(60,60))
        self.video_btn.setFixedSize(80,80)
        self.video_btn.setStyleSheet("border-radius: 40px; border:none; background-color: #2e2e2e;") 
        #self.video_btn.clicked.connect(self.capture_video)

        #pause button
        self.pause_btn = QPushButton()
        self.pause_btn.setIcon(QIcon("pictures/Pause.png"))
        self.pause_btn.setIconSize(QSize(60, 60))
        self.pause_btn.setFixedSize(80, 80)
        self.pause_btn.setStyleSheet("border-radius: 40px; border: none; background-color: #2e2e2e;")
        #self.pause_btn.clicked.connect(self.toggle_pause)
        self.pause_btn.hide()  # hidden at start

        #Creating a vertical layout for the buttons
        btn_layout = QVBoxLayout()
        btn_layout.addWidget(self.photo_btn)
        btn_layout.addWidget(self.video_btn)
        btn_layout.addWidget(self.pause_btn)
        btn_layout.addStretch()
        btn_layout.addSpacing(20)
        btn_layout.setContentsMargins(10,250,10,10)

        #Integrating the viewwindow and btn_layout
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.videoLabel)#left
        main_layout.addLayout(btn_layout)#right
        main_layout.setContentsMargins(10,10,10,10)

        # setting the final layout
        self.setLayout(main_layout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Camera_App()
    window.show()
    sys.exit(app.exec())



