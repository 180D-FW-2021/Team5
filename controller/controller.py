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

        #what the fuck is happening lol
        self.layout = QVBoxLayout() 
        self.gameover = QLabel("GAME OVER BRUH")
        self.layout.addWidget(self.gameover)
        #self.l1.setStyleSheet("QLabel {background-color: red;}")
        self.gameover.setAlignment(Qt.AlignCenter)
        self.outside = QLabel("reset da car and say continue")
        self.layout.addWidget(self.outside)
        self.points = QLabel(str(self.score))
        self.layout.addWidget(self.points)
        self.currentstate = QLabel(("CURRENT STATE: " + str(self.state)))
        self.layout.addWidget(self.currentstate)
        self.life = QLabel("YOU HAVE " + str(self.lives) + " lives")
        self.layout.addWidget(self.life)
        self.powa = QLabel("YOU GOT " + str(self.powerups) + " powerups")
        self.layout.addWidget(self.powa)

        self.gameover.show()
        self.outside.show()
        self.points.show()
        self.currentstate.show()
        self.life.show()
        self.powa.show()

        #clock clock clock
        self.timer = QTimer()

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
        self.mqtt.endGame()
        self.mqtt.stop()
        print("Shutting down")

    @pyqtSlot()
    def startGame(self):
        '''To be called only when starting game from a clean slate.'''
        print("Starting game")
        self.camera.start()
        self.speech.start()
        self.mqtt.startGame()
        self.state = GameState.RUNNING

    @pyqtSlot(QImage)
    def newFrame(self, frame):
        self.videoLabel.setPixmap(QPixmap.fromImage(frame))

    @pyqtSlot()
    def carOutside(self):
        if self.state != GameState.PAUSED:
            print("Car outside boundary")
            self.lives -= 1
            if self.lives == 0:
                self.gameover.show()
                self.outside.hide()
                self.points.hide()
                self.currentstate.hide()
                self.life.hide()
                self.powa.hide()

                self.mqtt.endGame()
                self.state = GameState.PAUSED
            else:
                self.gameover.hide()
                self.outside.show()
                self.points.show()
                self.currentstate.show()
                self.life.show()
                self.powa.show()

                self.mqtt.pauseGame()
                self.state = GameState.PAUSED

    @pyqtSlot()
    def dotCollected(self):
        if self.state != GameState.PAUSED:
            print("Car collected dot")
            self.score += 1
            # TODO: Update score on GUI
            self.mqtt.speedUp()

    @pyqtSlot(str)
    def keywordDetected(self, keyword):
        if keyword == "continue":
            if self.state == GameState.PAUSED:
                print("Continuing game")
                self.mqtt.startGame()
                self.state = GameState.RUNNING
                # TODO: make appropriate changes to GUI
                # the appropriate changes are: need to update da state
                # and put da score and da powa ups
                # truee
                # and put da lives 
                self.gameover.hide()
                self.outside.hide()
                self.points.show()
                self.currentstate.show()
                self.life.show()
                self.powa.show()
            else:
                # TODO: indicate on GUI that game is already running
                pass
        elif keyword == "game-pause":
            if self.state == GameState.RUNNING:
                print("Pausing game")
                self.mqtt.pauseGame()
                self.state == GameState.PAUSED
                # TODO: make appropriate changes to GUI
                self.gameover.hide()
                self.outside.hide()
                self.points.show()
                self.currentstate.show()
                self.life.show()
                self.powa.show()
            else:
                # TODO: indicate on GUI that game is already paused
                #hopefully self.currentstate updates
                pass
        elif keyword == "activate-power":
            if self.powerups > 0:
                print("Powerup")
                self.powerups -= 1
                self.mqtt.activatePower()
                # TODO: implement powerup, show powerup usage on GUI
                self.gameover.hide()
                self.outside.hide()
                self.points.show()
                self.currentstate.show()
                self.life.show()
                self.powa.show()
            else:
                # TODO: indicate on GUI that user has no powerups
                self.powa.setStyleSheet("QLabel {background-color: red;}")
                self.timer.singleShot(2*1000)
                self.powa.setStyleSheet("QLabel {background-color: white;}")
                pass
        else:
            print("Unknown keyword detected: %s" % keyword)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    root = MainWindow()
    root.show()
    sys.exit(app.exec())
