import cv2
import sys
import random
from PyQt6.QtWidgets import QApplication, QPushButton, QLabel,QHBoxLayout, QVBoxLayout, QWidget, QMessageBox
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
        self.photo_btn.clicked.connect(self.capture_photo)

        #Video button
        self.video_btn = QPushButton()
        self.video_btn.setIcon(QIcon("pictures/Video.png"))
        self.video_btn.setIconSize(QSize(60,60))
        self.video_btn.setFixedSize(80,80)
        self.video_btn.setStyleSheet("border-radius: 40px; border:none; background-color: #2e2e2e;") 
        self.video_btn.clicked.connect(self.capture_video)

        #pause button
        self.pause_btn = QPushButton()
        self.pause_btn.setIcon(QIcon("pictures/Pause.png"))
        self.pause_btn.setIconSize(QSize(60, 60))
        self.pause_btn.setFixedSize(80, 80)
        self.pause_btn.setStyleSheet("border-radius: 40px; border: none; background-color: #2e2e2e;")
        self.pause_btn.clicked.connect(self.toggle_pause)
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

        #Timer to update the frames every 20ms about a 22 FPS
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(20)

        self.is_recording = False # True if recording
        self.is_paused = False # True if recording is paused
        self.out = None # Object for saving the video
        self.vfilename = None #video file
        self.pfilename = None #photo file
    
    def update_frame(self):
        ret, frame = self.cam.read()
        if ret:
            if self.is_recording and not self.is_paused and self.out:
                self.out.write(frame)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            qimg = QImage(frame.data, w, h, ch * w, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(qimg)
            pixmap = pixmap.scaled(self.videoLabel.width(), self.videoLabel.height(), Qt.AspectRatioMode.KeepAspectRatio)
            self.videoLabel.setPixmap(pixmap)

    def capture_photo(self):
        ret, frame = self.cam.read()
        if ret:
            self.pfilename = f"photo_{random.randint(1,999999)}.jpg"
            cv2.imwrite(self.pfilename, frame)
            QMessageBox.information(self, "Photo Captured", f"Saved as {self.pfilename}")

    def capture_video(self):
        if not self.is_recording:
            # Setting to capture the video
            width = int(self.cam.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.vfilename = f"video_{random.randint(1,999999)}.mp4"
            self.out = cv2.VideoWriter(self.vfilename,cv2.VideoWriter_fourcc(*'mp4v'),20,(width,height))
            #start recording
            self.is_recording=True
            self.video_btn.setIcon(QIcon('pictures/Stop.png'))
            self.pause_btn.show()
        else:
            # stop recording
            self.is_recording=False
            self.video_btn.setIcon(QIcon('pictures/Video.png'))
            self.pause_btn.hide()
            if self.out:
                self.out.release() # saving the video by releasing the camera capture output
            QMessageBox.information(self,"Recording stopped", f"Saved as {self.vfilename}")

    def toggle_pause(self):
        if not self.is_paused:
            self.is_paused=True
            self.pause_btn.setIcon(QIcon('pictures/Resume.png'))
            print("Recording Paused")
        else:
            self.is_paused = False
            self.pause_btn.setIcon(QIcon('pictures/Pause.png'))
            print("Recording Paused")

    def closeEvent(self, event):
        self.cam.release()
        if self.out:
            self.out.release()
        event.accept()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Camera_App()
    window.show()
    sys.exit(app.exec())



