# Based on https://www.codepile.net/pile/ey9KAnxn

import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from cameraworker import CameraWorker

class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()

        # Game logic variables
        self.lives = 3
        self.score = 0

        # Window layout
        self.vbl = QVBoxLayout()
        self.videoLabel = QLabel()
        self.vbl.addWidget(self.videoLabel)

        # Start button
        self.start = QPushButton("Arena Ready")
        self.start.clicked.connect(self.startVideo)
        self.vbl.addWidget(self.start)

        # Set up overhead camera thread, but wait for user input to start it
        self.camera = CameraWorker()
        self.camera.newFrame.connect(self.newFrame)
        self.camera.carOutside.connect(self.carOutside)
        self.camera.dotCollected.connect(self.dotCollected)
        
        self.setLayout(self.vbl)

    def startVideo(self):
        self.camera.start()

    def newFrame(self, frame):
        self.videoLabel.setPixmap(QPixmap.fromImage(frame))

    def carOutside(self):
        self.lives -= 1
        # TODO: Stop car, indicate that car needs to be reset and wait for
        # "Continue" to restart game

    def dotCollected(self):
        self.score += 1
        # TODO: Update score on GUI, push speed increment to car

if __name__ == "__main__":
    app = QApplication(sys.argv)
    root = MainWindow()
    root.show()
    sys.exit(app.exec())