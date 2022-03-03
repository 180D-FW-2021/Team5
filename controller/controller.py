# Based on https://www.codepile.net/pile/ey9KAnxn

from enum import Enum
import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import time

from cameraworker import CameraWorker
from speechworker import SpeechWorker
from mqtt import Mqtt
import website

class GameState(Enum):
    RUNNING = 0
    PAUSED = 1

class startSignal(QObject):
    signal = pyqtSignal()

class pauseSignal(QObject):
    signal = pyqtSignal()

class powerupSignal(QObject):
    signal = pyqtSignal()

class MainWindow(QMainWindow):
    def __init__(self, cam, mic):
        super(MainWindow, self).__init__()

        # Game logic variables
        self.lives = 3
        self.score = 0
        self.powerups = 3
        self.state = GameState.PAUSED

        # Set up overhead camera thread, but wait for user input to start it
        self.camera = CameraWorker(cam)
        self.camera.newFrame.connect(self.newFrame)
        self.camera.carOutside.connect(self.carOutside)
        self.camera.dotCollected.connect(self.dotCollected)

        # Set up speech recognition, but wait for user input to start it
        self.speech = SpeechWorker(mic)
        self.speech.keywordDetected.connect(self.keywordDetected)
        
        # Start MQTT connection
        self.mqtt = Mqtt()

        # clock clock clock
        self.timer = QTimer(self)

        #GUI
        self.guiStart()

    def guiStart(self):
        # GUI layout
        #init
        self.setWindowTitle('Beep boop want to drive')
        self.layout1 = QHBoxLayout()

        #video box / left side
        self.videoLabel = QLabel(self)
        self.layout1.addWidget(self.videoLabel)

        # right side
        self.layout2 = QVBoxLayout()
        
        # Start button
        self.startButton = QPushButton("Start Game")
        self.start_signal = startSignal()
        self.start_signal.signal.connect(self.startGame)
        self.layout2.addWidget(self.startButton)

        #
        self.currentState = QLabel("GAME STATE NOW: " + str(self.state.name), self)
        self.currentScore = QLabel("YOUR SCORE ARE: " + str(self.score), self)
        self.currentLives = QLabel("YOUR LIVES IS: " + str(self.lives), self)
        self.currentPower = QLabel("YOUR POWERUPS IS: " + str(self.powerups), self)
        self.tooltip = QLabel("Click \"Start Game\" to start.", self)

        #voice command buttons
        self.layout3 = QHBoxLayout()
        self.pauseButton = QPushButton("Continue/Pause")
        self.powerupButton = QPushButton("Activate Power")
        self.pause_signal = pauseSignal()
        self.pause_signal.signal.connect(self.pauseGame)
        self.powerup_signal = powerupSignal()
        self.powerup_signal.signal.connect(self.activatePowerup)

        self.layout3.addWidget(self.pauseButton)
        self.layout3.addWidget(self.powerupButton)

        self.layout2.addWidget(self.currentState)
        self.layout2.addWidget(self.currentScore)
        self.layout2.addWidget(self.currentLives)
        self.layout2.addWidget(self.currentPower)
        self.layout2.addWidget(self.tooltip)
        self.layout2.addLayout(self.layout3)
        self.layout1.addLayout(self.layout2)

        self.startButton.clicked.connect(self.emit_start)
        self.pauseButton.clicked.connect(self.emit_pause)
        self.powerupButton.clicked.connect(self.emit_powerup)
        self.hideLabels()
        
        widget = QWidget()
        widget.setLayout(self.layout1)
        self.setCentralWidget(widget)

    def closeEvent(self):
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
        if not self.camera.active:
            self.camera.start()
        if not self.speech.active:
            self.speech.start()
        self.mqtt.startGame()
        self.lives = 3
        self.score = 0
        self.powerups = 3
        self.state = GameState.RUNNING
        self.showLabels()
        self.updateGui()
        self.time_start = time.time()

    @pyqtSlot()
    def pauseGame(self):
        if self.state == GameState.RUNNING:
            self.keywordDetected("game-pause")
        else:
            self.keywordDetected("continue")

    @pyqtSlot()
    def activatePowerup(self):
        self.keywordDetected("activate-power")

    @pyqtSlot()
    def emit_start(self):
        self.start_signal.signal.emit()

    @pyqtSlot()
    def emit_pause(self):
        self.pause_signal.signal.emit()

    @pyqtSlot()
    def emit_powerup(self):
        self.powerup_signal.signal.emit()
        
    @pyqtSlot(QImage)
    def newFrame(self, frame):
        self.videoLabel.setPixmap(QPixmap.fromImage(frame))

    @pyqtSlot()
    def carOutside(self):
        if self.state != GameState.PAUSED:
            print("Car outside boundary")
            self.lives -= 1
            if self.lives <= 0:
                self.mqtt.endGame()
                self.state = GameState.PAUSED
                self.tooltip.setText("GAME OVER")
                self.redFlash(self.tooltip)
                #TODO: Add username input
                powerups_used = 3 + (self.score // 5) - self.powerups
                username = self.gameOver()
                website.publish(username, self.score, powerups_used, self.time_start)
                self.updateGui()
            else:
                self.mqtt.pauseGame()
                self.state = GameState.PAUSED
                self.tooltip.setText("Reset car and say \"CONTINUE\"")
                self.updateGui()

    @pyqtSlot()
    def dotCollected(self):
        if self.state != GameState.PAUSED:
            print("Car collected dot")
            self.score += 1
            if self.score % 5 == 0:
                self.powerups += 1
                self.tooltip.setText("New powerup obtained!")
                self.redFlash(self.powerups)
            # TODO: Update score on GUI // no change needed
            self.mqtt.speedUp()
            self.updateGui()

    @pyqtSlot(str)
    def keywordDetected(self, keyword):
        if keyword == "continue":
            if self.state == GameState.PAUSED:
                print("Continuing game")
                self.mqtt.startGame()
                self.state = GameState.RUNNING
                self.tooltip.setText("Say \"GAME PAUSE\" to pause")
                self.updateGui()
            else:
                self.redFlash(self.tooltip)
                self.updateGui()
        elif keyword == "game-pause":
            if self.state == GameState.RUNNING:
                print("Pausing game")
                self.mqtt.pauseGame()
                self.state = GameState.PAUSED
                self.tooltip.setText("Say \"CONTINUE\" to continue")
                self.updateGui()
            else:
                self.redFlash(self.tooltip)
                self.updateGui()
                
        elif keyword == "activate-power":
            if self.powerups > 0:
                print("Powerup")
                self.powerups -= 1
                self.mqtt.activatePower()
                self.tooltip.setText("POWERUP USED!")
                self.timer.singleShot(6000, lambda x=self.tooltip: x.setText("Say \"GAME PAUSE\" to pause"))
                self.updateGui()
            else:
                self.redFlash(self.currentPower)
                self.updateGui()
        else:
            print("Unknown keyword detected: %s" % keyword)

    @pyqtSlot(QLabel)
    def redFlash(self,label):
        self.timer.singleShot(5000, lambda x=label: x.setStyleSheet("QLabel {background-color: none;}"))
        self.timer.singleShot(1000, lambda x=label: x.setStyleSheet("QLabel {background-color: red;}"))

    def updateGui(self):
        self.currentState.setText("Game State: " + str(self.state.name))
        self.currentScore.setText("Score: " + str(self.score))
        self.currentLives.setText("Lives: " + str(self.lives))
        self.currentPower.setText("Powerups: " + str(self.powerups))

    def showLabels(self):
        self.currentState.show()
        self.currentScore.show()
        self.currentLives.show()
        self.currentPower.show()

    def hideLabels(self):
        self.currentState.hide()
        self.currentScore.hide()
        self.currentLives.hide()
        self.currentPower.hide()

    def gameOver(self):
        name, done = QInputDialog.getText(self, "name box", "Enter your name:")
        if done:
            return name
        

def run(cam=0, mic=0):
    '''Starts the GUI and begins the game.'''
    app = QApplication(sys.argv)
    root = MainWindow(cam, mic)
    root.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    run()