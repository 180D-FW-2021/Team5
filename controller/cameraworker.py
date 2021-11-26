# Based on https://www.codepile.net/pile/ey9KAnxn

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import cv2 as cv
from random import randint

from camera.overhead import Overhead

class CameraWorker(QThread):
    '''Thread that handles overhead camera operation.'''
    newFrame = pyqtSignal(QImage) # Signal for new frame
    carOutside = pyqtSignal() # Signal for car leaving boundary
    dotCollected = pyqtSignal() # Signal for car picking up the target dot

    def run(self):
        self.active = True
        self.overhead = Overhead(200)
        self.overhead.setup()
        target = self.newTarget(-1)
        while self.active:
            inBoundary, gotTarget = self.overhead.loop(target)
            if not inBoundary:
                self.carOutside.emit()
            if gotTarget:
                target = self.newTarget(target)
                self.dotCollected.emit()
            self.newFrame.emit(self.overhead.drawFrame())

    def stop(self):
        self.active = False
        self.quit()

    def formatFrame(self, frame):
        '''Take an OpenCv frame in BGR and convert it to a format that's
        friendly to use with a PyQt PixMap.'''
        frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        frame = cv.flip(frame, 1)
        qtFrame = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
        newFrame = qtFrame.scaled(640, 480, Qt.KeepAspectRatio)
        return newFrame

    def newTarget(lastTarget):
        '''Returns a new target dot index. Makes sure that the same dot is not
        chosen twice.'''
        target = randint(0, self.overhead.nDots - 1)
        while target == lastTarget:
            target = randint(0, self.overhead.nDots - 1)
        return target
