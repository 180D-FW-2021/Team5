import cv2 as cv
import numpy as np

class Overhead(object):
    def __init__(self, threshold):
        '''Initialize various member variables and parse the game arena'''

        # Colors for drawing
        self.red = [0,255,255]
        self.green = [60,255,255]
        self.blue = [125,255,255]
        self.purple = [150,255,255]

        # Color bounds
        # Must be numpy arrays for cv.inRange()
        self.redBotLow = np.uint8([0,50,50])
        self.redBotHigh = np.uint8([10,255,255])
        self.redTopLow = np.uint8([170,50,50])
        self.redTopHigh = np.uint8([180,255,255])
        self.greenLow = np.uint8([45,50,50])
        self.greenHigh = np.uint8([75,255,255])
        self.blueLow = np.uint8([100,50,50])
        self.blueHigh = np.uint8([130,255,255])

        # Other variables
        self.boundary = None # Boundary contour
        self.dots = None # List of dots in the arena
        self.target = -1 # Index of target dot in dots list
        self.threshold = threshold # Area threshold for parsing dots
        self.camera = cv.VideoCapture(1) # DroidCam handle
        
        # Parse the boundary and dots from the game arena
        self.setup()

    def getFrame(self):
        '''Gets a frame from the camera and converts it to HSV'''
        _, frame = self.camera.read()
        return cv.cvtColor(frame, cv.COLOR_BGR2HSV)

    def setup(self):
        '''Parses the game arena, capturing game boundary and dots. Assumes
        boundary is blue and dots are green'''
        # Keep taking frames until we've found a boundary and at least one dot
        while (self.boundary is None) or (not self.dots):
            frame = self.getFrame()

            # Get boundary
            blueObjects = cv.inRange(frame, self.blueLow, self.blueHigh)
            blueContours, _ = cv.findContours(blueObjects,
                                        cv.RETR_LIST,
                                        cv.CHAIN_APPROX_NONE)
            if blueContours:
                # Take the largest contour and make an approximation of it to
                # smooth the outline
                largestBlue = max(blueContours, key=cv.contourArea)
                epsilon = 0.01 * cv.arcLength(largestBlue, True)
                outline = cv.approxPolyDP(largestBlue, epsilon, True)
                self.boundary = outline

            # Get dots
            greenObjects = cv.inRange(frame, self.greenLow, self.greenHigh)
            greenContours, _ = cv.findContours(greenObjects,
                                            cv.RETR_LIST,
                                            cv.CHAIN_APPROX_SIMPLE)
            filteredContours = filter(lambda c: cv.contourArea(c) > self.threshold, greenContours)
            self.dots = [cv.minEnclosingCircle(c) for c in filteredContours]
