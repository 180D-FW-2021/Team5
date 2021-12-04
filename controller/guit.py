# test gui
from enum import Enum
import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtCore import *

import paho.mqtt.client as mqtt
from subscriber import Subscriber
from queue import Queue

class window(QWidget):
    def __init__(self):
        #class member variables
        self.message = ""
        self.q = Queue()
        self.subscriber = Subscriber(self.q)
        #random bullshit you need to do to init
        super(window, self).__init__()
        self.setGeometry(100, 100, 1000, 600)
        self.setWindowTitle('please work')

        #window layout
        self.layout = QVBoxLayout() 
        self.l1 = QLabel("hi there1")
        self.layout.addWidget(self.l1)
        self.l1.setStyleSheet("QLabel {background-color: red;}")
        self.l1.setAlignment(Qt.AlignCenter)
        self.l2 = QLabel("hi there2")
        self.layout.addWidget(self.l2)
        self.l3 = QLabel("hi there3")
        self.layout.addWidget(self.l3)
        self.l4 = QLabel("hi there4")
        self.layout.addWidget(self.l4)
        self.l5 = QLabel("hi there5")
        self.layout.addWidget(self.l5)
        self.l6 = QLabel("hi there6")
        self.layout.addWidget(self.l6)

        #cool and dank menu bar

        #start button
        self.start = QPushButton("Arena Ready")
        self.start.clicked.connect(self.startGame)
        self.layout.addWidget(self.start)

        #show message button
        #self.show = QPushButton("update button")
        #self.show.clicked.connect(self.showMessage)
        #self.layout.addWidget(self.show)

        #i don't know why you need to do this
        self.setLayout(self.layout)
        
    def startGame(self):
        '''To be called only when starting game from a clean slate.'''
        print("starting now")
        self.l1.setText("Button clicked")
        self.start.hide()

    def showMessage(self):
        self.l2.setText(self.message)
    
    def sub(self):
        client = self.subscriber.init()
        self.subscriber.run(client)
        try:
            while True:
                self.message = self.q.get()
                if self.message is None:
                    continue
                print("THE MESSAGE IS: " + self.message)
        except KeyboardInterrupt:
            self.subscriber.stop()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    root = window()
    root.show()
    sys.exit(app.exec())