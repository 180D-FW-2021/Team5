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

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # Game logic variables
        self.lives = 3
        self.score = 0
        self.powerups = 0
        self.state = GameState.PAUSED

        # Set up overhead camera thread, but wait for user input to start it
        self.camera = CameraWorker()
        self.camera.newFrame.connect(self.newFrame)
        self.camera.carOutside.connect(self.carOutside)
        self.camera.dotCollected.connect(self.dotCollected)

        # Set up speech recognition, but wait for user input to start it
        self.speech = SpeechWorker()
        self.speech.keywordDetected.connect(self.keywordDetected)
        
        # Start MQTT connection
        self.mqtt = Mqtt()

        # clock clock clock
        self.timer = QTimer(self)

        # GUI layout
        #init
        self.setGeometry(100, 100, 1000, 600)
        self.setWindowTitle('please work')
        self.layout1 = QHBoxLayout()

        #video box / left side
        self.videoLabel = QLabel(self)
        self.layout1.addWidget(self.videoLabel)

        # right side
        self.layout2 = QVBoxLayout()
        # Start button
        self.start = QPushButton("Arena Ready")
        self.start.clicked.connect(self.startGame)
        self.layout2.addWidget(self.start)

        self.currentState = QLabel("GAME STATE NOW: " + str(self.state), self)
        self.currentScore = QLabel("YOUR SCORE ARE: " + str(self.score), self)
        self.currentLives = QLabel("YOUR LIVES IS: " + str(self.lives), self)
        self.currentPower = QLabel("YOUR POWERUPS IS: " + str(self.powerups), self)
        self.tooltip = QLabel("Say \"GAME PAUSE\" to pause", self)

        self.layout2.addWidget(self.currentState)
        self.layout2.addWidget(self.currentScore)
        self.layout2.addWidget(self.currentLives)
        self.layout2.addWidget(self.currentPower)
        self.layout2.addWidget(self.tooltip)
        self.layout1.addLayout(self.layout2)
        
        widget = QWidget()
        widget.setLayout(self.layout1)
        self.setCentralWidget(widget)

    def closeEvent(self, event):
        '''Clean up all necessary components when the user closes the main
        window.'''
        #self.camera.stop()
        #self.speech.stop()
        self.mqtt.stop()
        print("Shutting down")

    def startGame(self):
        '''To be called only when starting game from a clean slate.'''
        print("Starting game")
        #self.camera.start()
        #self.speech.start()

    def newFrame(self, frame):
        self.videoLabel.setPixmap(QPixmap.fromImage(frame))

    def carOutside(self):
        print("Car outside boundary")
        self.lives -= 1
        if self.lives == 0:
            # TODO: Update GUI to say game over
            self.mqtt.endGame()
            self.state = GameState.PAUSED
            self.tooltip.setText("GAME OVER")
            self.redFlash(self.tooltip)
        else:
            # TODO: Update GUI to tell user to reset car and say "Continue"
            self.mqtt.pauseGame()
            self.state = GameState.PAUSED
            self.tooltip.setText("Reset car and say \"CONTINUE\"")

    def dotCollected(self):
        print("Car collected dot")
        self.score += 1
        # TODO: Update score on GUI // no change needed
        self.mqtt.speedUp()

    def keywordDetected(self, keyword):
        if keyword == "continue":
            if self.state == GameState.PAUSED:
                self.mqtt.startGame()
                # TODO: make appropriate changes to GUI
                self.tooltip.setText("Say \"GAME PAUSE\" to pause")
            else:
                # TODO: indicate on GUI that game is already running
                self.redFlash(self.tooltip)
        elif keyword == "game-pause":
            if self.state == GameState.RUNNING:
                self.mqtt.pauseGame()
                # TODO: make appropriate changes to GUI
                self.tooltip.setText("Say \"CONTINUE\" to continue")
            else:
                # TODO: indicate on GUI that game is already paused
                self.redFlash(self.tooltip)
        elif keyword == "activate-power":
            if self.powerups > 0:
                self.powerups -= 1
                # TODO: implement powerup, show powerup usage on GUI
                self.tooltip.setText("POWERUP USED!")
                self.timer.singleShot(6000, lambda x=self.tooltip: x.setText("Say \"GAME PAUSE\" to pause"))
            else:
                # TODO: indicate on GUI that user has no powerups
                self.redFlash(self.currentPower)
        else:
            print("Unknown keyword detected: %s" % keyword)

    def redFlash(self,label):
        self.timer.singleShot(5000, lambda x=label: x.setStyleSheet("QLabel {background-color: none;}"))
        self.timer.singleShot(1000, lambda x=label: x.setStyleSheet("QLabel {background-color: red;}"))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    root = MainWindow()
    root.show()
    sys.exit(app.exec())
