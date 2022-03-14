import numpy as np
import cv2 as cv
from PyQt5.QtGui import QImage
from PyQt5.QtCore import QThread, pyqtSignal, Qt

class Overhead(object):
    def __init__(self):
        self.cap = cv.VideoCapture(0) 
        self.frame = None
        self.active = False

class CameraWorker(QThread):
    newFrame = pyqtSignal(QImage) # Signal for new frame

    def run(self):
        self.active = True
        self.camera = Overhead()
        while self.active == True:
            formattedFrame = self.formatFrame(self.drawFrame())
            self.newFrame.emit(formattedFrame)

    def formatFrame(self, frame):
        '''Take an OpenCv frame in BGR and convert it to a format that's
        friendly to use with a PyQt PixMap.'''
        frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        frame = cv.flip(frame, 1)
        self.frame = frame.copy() # Make a copy and keep a reference so GUI doesn't segfault later
        qtFrame = QImage(self.frame.data, self.frame.shape[1], self.frame.shape[0], QImage.Format_RGB888)
        newFrame = qtFrame.scaled(640, 480, Qt.KeepAspectRatio)
        return newFrame

    def drawFrame(self):
        ret, frame = self.camera.cap.read()
        return cv.cvtColor(frame, cv.COLOR_HSV2BGR)

    def stop(self):
        # When everything done, release the capture
        self.active = False
        self.cap.release()
        cv.destroyAllWindows()