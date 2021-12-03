# Based on https://www.codepile.net/pile/ey9KAnxn

from enum import Enum
import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from cameraworker import CameraWorker
from speechworker import SpeechWorker
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

        # Set up speech recognition, but wait for user input to start it
        self.speech = SpeechWorker()
        self.speech.keywordDetected.connect(self.keywordDetected)
        
        self.setLayout(self.vbl)

    def closeEvent(self, event):
        '''Clean up all necessary components when the user closes the main
        window.'''
        self.camera.stop()
        self.speech.stop()
        self.mqtt.stop()
        print("Shutting down")

    @pyqtSlot()
    def startGame(self):
        '''To be called only when starting game from a clean slate.'''
        print("Starting game")
        self.camera.start()
        self.speech.start()

    @pyqtSlot(QImage)
    def newFrame(self, frame):
        self.videoLabel.setPixmap(QPixmap.fromImage(frame))

    @pyqtSlot()
    def carOutside(self):
        print("Car outside boundary")
        self.lives -= 1
        if self.lives == 0:
            # TODO: Update GUI to say game over
            self.mqtt.endGame()
            self.state = GameState.PAUSED
        else:
            # TODO: Update GUI to tell user to reset car and say "Continue"
            self.mqtt.pauseGame()
            self.state = GameState.PAUSED

    @pyqtSlot()
    def dotCollected(self):
        print("Car collected dot")
        self.score += 1
        # TODO: Update score on GUI
        self.mqtt.speedUp()

    @pyqtSlot(str)
    def keywordDetected(self, keyword):
        if keyword == "continue":
            if self.state == GameState.RUNNING:
                self.mqtt.startGame()
                # TODO: make appropriate changes to GUI
            else:
                # TODO: indicate on GUI that game is already running
                pass
        elif keyword == "game-pause":
            if self.state == GameState.PAUSED:
                self.mqtt.pauseGame()
                # TODO: make appropriate changes to GUI
            else:
                # TODO: indicate on GUI that game is already paused
                pass
        elif keyword == "activate-power":
            if self.powerups > 0:
                self.powerups -= 1
                # TODO: implement powerup, show powerup usage on GUI
            else:
                # TODO: indicate on GUI that user has no powerups
                pass
        else:
            print("Unknown keyword detected: %s" % keyword)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    root = MainWindow()
    root.show()
    sys.exit(app.exec())