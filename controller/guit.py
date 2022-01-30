# test gui
from enum import Enum
import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtCore import *

from testcamera import CameraWorker

class GameState(Enum):
    RUNNING = 0
    PAUSED = 1
    GAME_OVER_BITCH = 2
    #SUPER_FUCKING_FAST = 2

class Label(QWidget):
    def __init__(self, text=""):
        super(Label, self).__init__()
        self.label = QLabel(text)

class Signal(QObject):
    started = pyqtSignal()

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # Game logic variables
        self.lives = 3
        self.score = 0
        self.powerups = 0
        self.state = GameState.PAUSED
        

        #random bullshit you need to do to init

        self.setGeometry(100, 100, 1000, 600)
        self.setWindowTitle('please work')
        
        #
        self.layout1 = QHBoxLayout()

        #camera
        self.camera = CameraWorker()
        self.camera.newFrame.connect(self.newFrame)
        self.videoLabel = QLabel(self)
        self.layout1.addWidget(self.videoLabel)

        #start button
        self.start_signal = Signal()
        self.start_signal.started.connect(self.startGame)

        self.layout2 = QVBoxLayout()
        self.start = QPushButton("go pikachu i choose you")
        
        self.layout2.addWidget(self.start)
        self.timer = QTimer(self)

        #text and shit
        
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
        
        self.start.clicked.connect(self.emit_start)

        widget = QWidget()
        widget.setLayout(self.layout1)
        self.setCentralWidget(widget)

        
        #i don't know why you need to do this
        #self.setLayout(self.layout)

    @pyqtSlot()
    def startGame(self):
        '''To be called only when starting game from a clean slate.'''
        print("starting now")
        self.camera.start()
        self.start.hide()
        self.showLabels()
        self.redFlash(self.currentState)

    @pyqtSlot(QLabel)
    def redFlash(self,label):
        self.timer.singleShot(5000, lambda x=label: x.setStyleSheet("QLabel {background-color: none;}"))
        self.timer.singleShot(1000, lambda x=label: x.setStyleSheet("QLabel {background-color: red;}"))
        print("flashed")

    @pyqtSlot()
    def emit_start(self):
        self.start_signal.started.emit()

    def showMessage(self):
        self.l2.setText(self.message)

    @pyqtSlot(QImage)
    def newFrame(self, frame):
        self.videoLabel.setPixmap(QPixmap.fromImage(frame))

    def showLabels(self):
        self.currentState.show()
        self.currentScore.show()
        self.currentLives.show()
        self.currentPower.show()
        self.tooltip.show()

    def hideLabels(self):
        self.currentState.hide()
        self.currentScore.hide()
        self.currentLives.hide()
        self.currentPower.hide()
        self.tooltip.hide()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    root = MainWindow()
    root.show()
    sys.exit(app.exec())