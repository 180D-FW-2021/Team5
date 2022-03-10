# Based on https://www.codepile.net/pile/ey9KAnxn

from enum import Enum
import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import time

from cameraworker import CameraWorker
from speechworker import SpeechWorker

from mqtt import ControllerMqtt
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
        self.nLives = 3
        self.nScore = 0
        self.nPower = 3
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
        self.mqtt = ControllerMqtt()

        # Heartbeat timer
        self.heartbeat = QTimer()
        self.heartbeat.timeout.connect(self.mqtt.heartbeat)
        self.heartbeat.start(1000)

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

        #game information labels
        self.stateLabel = QLabel("GAME STATE NOW: " + str(self.state.name), self)
        self.scoreLabel = QLabel("YOUR SCORE ARE: " + str(self.nScore), self)
        self.livesLabel = QLabel("YOUR LIVES IS: " + str(self.nLives), self)
        self.powerLabel = QLabel("YOUR POWERUPS IS: " + str(self.nPower), self)
        self.tipLabel = QLabel("Click \"Start Game\" to start.", self)

        #voice command buttons
        self.layout3 = QHBoxLayout()
        self.pauseButton = QPushButton("Continue/Pause")
        self.powerupButton = QPushButton("Activate Power")
        self.pauseSignal = pauseSignal()
        self.pauseSignal.signal.connect(self.pauseGame)
        self.powerupSignal = powerupSignal()
        self.powerupSignal.signal.connect(self.activatePowerup)

        self.layout3.addWidget(self.pauseButton)
        self.layout3.addWidget(self.powerupButton)

        self.layout2.addWidget(self.stateLabel)
        self.layout2.addWidget(self.scoreLabel)
        self.layout2.addWidget(self.livesLabel)
        self.layout2.addWidget(self.powerLabel)
        self.layout2.addWidget(self.tipLabel)
        self.layout2.addLayout(self.layout3)
        self.layout1.addLayout(self.layout2)

        self.startButton.clicked.connect(self.emit_start)
        self.pauseButton.clicked.connect(self.emit_pause)
        self.powerupButton.clicked.connect(self.emit_powerup)
        self.hideLabels()
        
        widget = QWidget()
        widget.setLayout(self.layout1)
        self.setCentralWidget(widget)

    def closeEvent(self, event):
        '''Clean up all necessary components when the user closes the main
        window.'''
        self.camera.stop()
        self.speech.stop()
        self.mqtt.endGame()
        self.mqtt.stop()
        print("Shutting down")
        event.accept()

    @pyqtSlot()
    def startGame(self):
        '''To be called only when starting game from a clean slate.'''
        print("Starting game")
        if not self.camera.active:
            self.camera.start()
        if not self.speech.active:
            self.speech.start()
        self.mqtt.startGame()
        self.nLives = 3
        self.nScore = 0
        self.nPower = 3
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
        self.pauseSignal.signal.emit()

    @pyqtSlot()
    def emit_powerup(self):
        self.powerupSignal.signal.emit()
        
    @pyqtSlot(QImage)
    def newFrame(self, frame):
        self.videoLabel.setPixmap(QPixmap.fromImage(frame))

    @pyqtSlot()
    def carOutside(self):
        if self.state != GameState.PAUSED:
            print("Car outside boundary")
            self.nLives -= 1
            if self.nLives <= 0:
                self.mqtt.endGame()
                self.state = GameState.PAUSED
                self.tipLabel.setText("GAME OVER")
                self.redFlash(self.tipLabel)
                #TODO: Add username input
                powerups_used = 3 + (self.nScore // 5) - self.nPower
                self.camera.freeze = True
                username = self.gameOver()
                while self.mqtt.nTurns == -1:
                    pass
                website.publish(username, self.nScore, powerups_used, self.mqtt.nTurns, self.time_start)
                self.mqtt.nTurns = -1
                self.camera.freeze = False
                self.updateGui()
            else:
                self.mqtt.pauseGame()
                self.state = GameState.PAUSED
                self.tipLabel.setText("Reset car and say \"CONTINUE\"")
                self.updateGui()

    @pyqtSlot()
    def dotCollected(self):
        if self.state != GameState.PAUSED:
            print("Car collected dot")
            self.nScore += 1
            if self.nScore % 5 == 0:
                self.nPower += 1
                self.tipLabel.setText("New powerup obtained!")
                self.redFlash(self.powerLabel)
            self.mqtt.speedUp()
            self.updateGui()

    @pyqtSlot(str)
    def keywordDetected(self, keyword):
        if keyword == "continue":
            if self.state == GameState.PAUSED:
                print("Continuing game")
                self.mqtt.startGame()
                self.state = GameState.RUNNING
                self.tipLabel.setText("Say \"GAME PAUSE\" to pause")
                self.updateGui()
            else:
                self.redFlash(self.tipLabel)
                self.updateGui()
        elif keyword == "game-pause":
            if self.state == GameState.RUNNING:
                print("Pausing game")
                self.mqtt.pauseGame()
                self.state = GameState.PAUSED
                self.tipLabel.setText("Say \"CONTINUE\" to continue")
                self.updateGui()
            else:
                self.redFlash(self.tipLabel)
                self.updateGui()
                
        elif keyword == "activate-power":
            if self.nPower > 0:
                print("Powerup")
                self.nPower -= 1
                self.mqtt.activatePower()
                self.tipLabel.setText("POWERUP USED!")
                self.timer.singleShot(6000, lambda x=self.tipLabel: x.setText("Say \"GAME PAUSE\" to pause"))
                self.updateGui()
            else:
                self.redFlash(self.powerLabel)
                self.updateGui()
        else:
            print("Unknown keyword detected: %s" % keyword)

    @pyqtSlot(QLabel)
    def redFlash(self,label):
        self.timer.singleShot(5000, lambda x=label: x.setStyleSheet("QLabel {background-color: none;}"))
        self.timer.singleShot(1000, lambda x=label: x.setStyleSheet("QLabel {background-color: red;}"))

    def updateGui(self):
        self.stateLabel.setText("Game State: " + str(self.state.name))
        self.scoreLabel.setText("Score: " + str(self.nScore))
        self.livesLabel.setText("Lives: " + str(self.nLives))
        self.powerLabel.setText("Powerups: " + str(self.nPower))

    def showLabels(self):
        self.stateLabel.show()
        self.scoreLabel.show()
        self.livesLabel.show()
        self.powerLabel.show()
        self.pauseButton.show()
        self.powerupButton.show()

    def hideLabels(self):
        self.stateLabel.hide()
        self.scoreLabel.hide()
        self.livesLabel.hide()
        self.powerLabel.hide()
        self.pauseButton.hide()
        self.powerupButton.hide()

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