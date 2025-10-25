import cv2
import sys
import os
import random
import numpy as np
import sounddevice as sd
import soundfile as sf
import threading
import imageio_ffmpeg as ffmpeg
import subprocess
from PyQt6.QtWidgets import QApplication, QPushButton, QLabel,QHBoxLayout, QVBoxLayout, QWidget, QMessageBox, QScrollArea
from PyQt6.QtCore import QSize, Qt, QTimer
from PyQt6.QtGui import QImage, QIcon, QPixmap

class Camera_App(QWidget): #Inherits basic GUI window
    def __init__(self):
        super().__init__()
        #window setting
        self.setWindowTitle("PyCam")
        self.setStyleSheet("background-color: #1e1e1e; color: white")
        self.setFixedSize(1280,720)
        
        #Camera setting
        self.cam = cv2.VideoCapture(0)
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        #Webcam view setting 
        self.videoLabel = QLabel()
        self.videoLabel.setFixedSize(910,540)
        self.videoLabel.setStyleSheet("background-color: black; border: 2px solid #444; border-radius: 20px")

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

        #Timer for the video
        self.video_timer = QLabel("00:00")
        self.video_timer.setStyleSheet("color: red; font-size: 24px; font-weight: bold;")
        self.video_timer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_timer.setFixedSize(70,100)
        self.video_timer.hide()

        #Filters
        self.active_filter="Normal"
        self.active_filter_btn= None

        # Filter Buttons in a layout
        self.filter_btn = QWidget()
        self.filter_layout = QVBoxLayout(self.filter_btn)
        self.filter_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        #Adding a label at the top of the widget.
        self.filter_label = QLabel("Filters")
        self.filter_label.setStyleSheet("color: #5a9bd5; font-size: 20px;")
        self.filter_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.filter_layout.addWidget(self.filter_label)

        # filters and icons
        self.filters = {
            "Normal": "pictures/Normal.png",
            "Grayscale": "pictures/GrayScale.png",
            "Sepia": "pictures/Sepia.png",
            "Cartoon": "pictures/Cartoon.png",
            "Blur":"pictures/Blur.png"
        }

        #A loop to create individual filter buttons and add them in the layout created
        for name, icon_path in self.filters.items():
            # A label of filter name for each filter 
            fllbl = QLabel(name)
            fllbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            fllbl.setStyleSheet("color: white; font-size: 14px;")
            # Button for each filter
            btn = QPushButton()
            btn.setIcon(QIcon(icon_path))
            btn.setFixedSize(170,170)
            btn.setIconSize(QSize(150,150))
            btn.setStyleSheet("border: none; background-color: #3a3a3a;")
            btn.clicked.connect(lambda _, n=name,b=btn: self.set_filter(n,b))
            if name == "Normal":
                self.set_filter(name,btn)
            #Adding label and button in layout
            self.filter_layout.addWidget(fllbl)
            self.filter_layout.addWidget(btn)
            self.filter_layout.addSpacing(2)
            self.filter_layout.setContentsMargins(0,0,0,0)
        
        #Making the filters scrollable
        self.filter_scroll=QScrollArea()
        self.filter_scroll.setWidgetResizable(True)
        self.filter_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.filter_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.filter_scroll.setWidget(self.filter_btn)
        self.filter_scroll.setFixedWidth(170)
        self.filter_scroll.setStyleSheet("background-color: #2a2a2a; border: none;")
        


        #Creating a vertical layout for the buttons
        btn_layout = QVBoxLayout()
        btn_layout.addWidget(self.photo_btn)
        btn_layout.addSpacing(15)
        btn_layout.addWidget(self.video_btn)
        btn_layout.addSpacing(15)
        btn_layout.addWidget(self.pause_btn)
        btn_layout.addWidget(self.video_timer)
        btn_layout.addStretch()
        btn_layout.setContentsMargins(10,200,10,10)

        #Integrating the viewwindow and btn_layout and filter_layout
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.videoLabel)#left
        main_layout.addLayout(btn_layout)#Middle
        main_layout.addWidget(self.filter_scroll)#right
        main_layout.setContentsMargins(10,10,10,10)

        # setting the final layout
        self.setLayout(main_layout)

        #Timer to update the frames every 20ms about a 22 FPS
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(31)

        
        self.is_recording = False # True if recording
        self.is_paused = False # True if recording is paused
        self.out = None # Object for saving the video
        self.vfilename = None #video file
        self.pfilename = None #photo file
        self.record_seconds = 0
        self.timer_count = QTimer()
        self.timer_count.timeout.connect(self.update_timer)
        self.afilename = None #Temporary audio file
        self.finalname = None #Merged final video
        self.audio_thread = None #Thread for recording audio
        self.audio_frames = []  #To store audio data
    
    def update_frame(self):
        ret, frame = self.cam.read()
        if ret:
            frame = self.apply_filter(frame, self.active_filter)

            if self.is_recording and not self.is_paused and self.out:
                self.out.write(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

            if len(frame.shape) == 2:  # Grayscale case
                qimg = QImage(frame.data, frame.shape[1], frame.shape[0], frame.shape[1],
                              QImage.Format.Format_Grayscale8)
            else: # All other cases
                qimg = QImage(frame.data, frame.shape[1], frame.shape[0], frame.shape[1]*3,
                              QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(qimg)
            pixmap = pixmap.scaled(self.videoLabel.width(), self.videoLabel.height(), Qt.AspectRatioMode.KeepAspectRatio)
            self.videoLabel.setPixmap(pixmap)

    def set_filter(self,name,btn):
        if self.active_filter_btn:
            self.active_filter_btn.setStyleSheet("border: none; background-color: #3a3a3a;")
        self.active_filter_btn = btn
        self.active_filter = name
        btn.setStyleSheet("border: none; background-color: #5a9bd5;")  # blue tint
        print(f"Filter applied: {name}")
        
    def apply_filter(self,frame,filter_name):

        if filter_name == "Grayscale":
            return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        elif filter_name == "Sepia":
            sepia = cv2.transform(frame, np.array([
                [0.272, 0.534, 0.131],
                [0.349, 0.686, 0.168],
                [0.393, 0.769, 0.189]
            ]))
            sepia = np.clip(sepia,0,255).astype(np.uint8)
            return cv2.cvtColor(sepia, cv2.COLOR_BGR2RGB)
        
        elif filter_name == "Cartoon":
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.medianBlur(gray, 5)
            edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                          cv2.THRESH_BINARY, 9, 9)
            color = cv2.bilateralFilter(frame, 9, 250, 250)
            cartoon = cv2.bitwise_and(color, color, mask=edges)
            return cv2.cvtColor(cartoon, cv2.COLOR_BGR2RGB)
        
        elif filter_name=="Blur":
            return cv2.GaussianBlur(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), (15,15), 0)
        else:
            return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
    def record_audio(self):
        fs = 44100 
        self.audio_frames = []
        def callback(indata, frames, time, status):
            if self.is_recording and not self.is_paused:
                self.audio_frames.append(indata.copy())

        with sd.InputStream(samplerate=fs, channels=2, callback=callback):
            while self.is_recording:
                sd.sleep(100)
        audio_data = np.concatenate(self.audio_frames, axis=0)

        sf.write(self.afilename, audio_data, fs)

    def merge_audio_video(self):
        ffmpeg_path = ffmpeg.get_ffmpeg_exe()
        command = [
            ffmpeg_path,
            "-y",
            "-i", self.vfilename,    
            "-i", self.afilename,      
            "-c:v", "copy",
            "-c:a", "aac",
            "-strict", "experimental",
            self.finalname
        ]
        
        try:
            subprocess.run(command, check=True)
            print(f"Merged file saved as {self.finalname}")
        except subprocess.CalledProcessError as e:
            print(f"Error merging: {e}")

    def update_timer(self):
        self.record_seconds+=1
        mins,secs = divmod(self.record_seconds, 60)
        self.video_timer.setText(f"{mins:02d}:{secs:02d}")

    def capture_photo(self):
        ret, frame = self.cam.read()
        if ret:
            self.pfilename = f"photo_{random.randint(1,999999)}.jpg"
            cv2.imwrite(self.pfilename, frame)
            QMessageBox.information(self, "Photo Captured", f"Saved as {self.pfilename}")

    def capture_video(self):
        if not self.is_recording:
            width = int(self.cam.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.vfilename = f"temp_{random.randint(1,999999)}.mp4"
            self.afilename = f"audio_{random.randint(1,999999)}.wav"
            self.finalname = f"video_{random.randint(1,999999)}.mp4"
            self.audio_thread = threading.Thread(target=self.record_audio)
            self.audio_thread.start()
            self.is_recording = True
            self.out = cv2.VideoWriter(self.vfilename, cv2.VideoWriter_fourcc(*'mp4v'), 31, (width, height))
            self.record_seconds = 0
            self.video_timer.setText("00:00")
            self.video_timer.show()
            self.timer_count.start(1000)
            self.video_btn.setIcon(QIcon("pictures/Stop.png"))
            self.pause_btn.show()

        else:

            self.is_recording = False
            if self.audio_thread:
                self.audio_thread.join()
            self.video_btn.setIcon(QIcon("pictures/Video.png"))
            self.pause_btn.hide()
            self.video_timer.hide()
            self.timer_count.stop()
            if self.out:
                self.out.release()

            self.merge_audio_video()
            os.remove(self.vfilename)
            os.remove(self.afilename)
            QMessageBox.information(self, "Recording Stopped", f"Saved as {self.finalname}")

    def toggle_pause(self):
        if not self.is_paused:
            self.is_paused=True
            self.pause_btn.setIcon(QIcon('pictures/Resume.png'))
            print("Recording Paused")
            self.timer_count.stop()
        else:
            self.is_paused = False
            self.pause_btn.setIcon(QIcon('pictures/Pause.png'))
            print("Recording Paused")
            self.timer_count.start(1000)

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



