# Based on https://www.codepile.net/pile/ey9KAnxn

from enum import Enum
import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from cameraworker import CameraWorker
from mqtt import Mqtt

class GameState(Enum):
    RUNNING = 0
    PAUSED = 1

class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()

        # Game logic variables
        self.lives = 3
        self.score = 0
        self.powerups = 0
        self.state = GameState.PAUSED

        # Window layout
        self.vbl = QVBoxLayout()
        self.videoLabel = QLabel()
        self.vbl.addWidget(self.videoLabel)

        # Start button
        self.start = QPushButton("Arena Ready")
        self.start.clicked.connect(self.startGame)
        self.vbl.addWidget(self.start)

        # Start MQTT connection
        self.mqtt = Mqtt()

        # Set up overhead camera thread, but wait for user input to start it
        self.camera = CameraWorker()
        self.camera.newFrame.connect(self.newFrame)
        self.camera.carOutside.connect(self.carOutside)
        self.camera.dotCollected.connect(self.dotCollected)
        
        self.setLayout(self.vbl)

    def closeEvent(self, event):
        '''Clean up all necessary components when the user closes the main
        window.'''
        self.mqtt.stop()

    def startGame(self):
        '''To be called only when starting game from a clean slate.'''
        self.camera.start()

    def newFrame(self, frame):
        self.videoLabel.setPixmap(QPixmap.fromImage(frame))

    def carOutside(self):
        self.lives -= 1
        if self.lives == 0:
            # TODO: Update GUI to say game over
            self.mqtt.endGame()
            self.state = GameState.PAUSED
        else:
            # TODO: Update GUI to tell user to reset car and say "Continue"
            self.mqtt.pauseGame()
            self.state = GameState.PAUSED

    def dotCollected(self):
        self.score += 1
        # TODO: Update score on GUI
        self.mqtt.speedUp()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    root = MainWindow()
    root.show()
    sys.exit(app.exec())