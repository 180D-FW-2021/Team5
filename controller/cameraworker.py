# Based on https://www.codepile.net/pile/ey9KAnxn

from PyQt5.QtGui import QImage
from PyQt5.QtCore import QThread, pyqtSignal, Qt
import cv2 as cv
from random import randint

# From https://stackoverflow.com/questions/714063/importing-modules-from-parent-folder
import os
import sys
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from camera.overhead import Overhead

class CameraWorker(QThread):
    '''Thread that handles overhead camera operation.'''
    newFrame = pyqtSignal(QImage) # Signal for new frame
    carOutside = pyqtSignal() # Signal for car leaving boundary
    dotCollected = pyqtSignal() # Signal for car picking up the target dot

    def __init__(self, index):
        super().__init__()
        # Store camera device index on construction
        self.index = index
        self.active = False

    def run(self):
        self.active = True
        self.overhead = Overhead(self.index)
        self.overhead.setup()
        target = self.newTarget(-1)
        while self.active:
            inBoundary, gotTarget = self.overhead.loop(target)
            if not inBoundary:
                self.carOutside.emit()
            if gotTarget:
                target = self.newTarget(target)
                self.dotCollected.emit()
            formattedFrame = self.formatFrame(self.overhead.drawFrame(car=True, boundary=True))
            self.newFrame.emit(formattedFrame)

    def stop(self):
        self.active = False
        if self.overhead:
            self.overhead.stop()
        self.quit()

    def formatFrame(self, frame):
        '''Take an OpenCv frame in BGR and convert it to a format that's
        friendly to use with a PyQt PixMap.'''
        frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        self.frame = frame.copy() # Make a copy and keep a reference so GUI doesn't segfault later
        qtFrame = QImage(self.frame.data, self.frame.shape[1], self.frame.shape[0], QImage.Format_RGB888)
        newFrame = qtFrame.scaled(640, 480, Qt.KeepAspectRatio)
        return newFrame

    def newTarget(self, lastTarget):
        '''Returns a new target dot index. Makes sure that the same dot is not
        chosen twice.'''
        target = randint(0, self.overhead.nDots - 1)
        while target == lastTarget:
            target = randint(0, self.overhead.nDots - 1)
        return target
