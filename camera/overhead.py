import cv2 as cv
import numpy as np

class Overhead(object):
    def __init__(self, threshold):
        '''Initialize various member variables and parse the game arena.'''

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
        self.nDots = -1 # Number of dots parsed in the arena
        self.target = -1 # Index of target dot in dots list
        self.threshold = threshold # Area threshold for parsing dots
        self.camera = cv.VideoCapture(1) # DroidCam handle
        self.frame = None # Current frame being processed
        
        # Parse the boundary and dots from the game arena
        self.setup()

    def getFrame(self):
        '''Gets a frame from the camera, converts it to HSV, and stores it in
        self.frame.'''
        _, frame = self.camera.read()
        return cv.cvtColor(frame, cv.COLOR_BGR2HSV)

    def setup(self):
        '''Parses the game arena, capturing game boundary and dots. Assumes
        boundary is blue and dots are green.'''
        # Keep taking frames until we've found a boundary and at least one dot
        while (self.boundary is None) or (not self.dots):
            self.getFrame()

            # Get boundary
            blueObjects = cv.inRange(self.frame, self.blueLow, self.blueHigh)
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
            greenObjects = cv.inRange(self.frame, self.greenLow, self.greenHigh)
            greenContours, _ = cv.findContours(greenObjects,
                                            cv.RETR_LIST,
                                            cv.CHAIN_APPROX_SIMPLE)
            filteredContours = filter(lambda c: cv.contourArea(c) > self.threshold, greenContours)
            self.dots = [cv.minEnclosingCircle(c) for c in filteredContours]
            self.nDots = len(self.dots)

    def loop(self, target):
        '''Main function to be called each game loop. Takes in the index of
        current target in dots list. Finds the car and sees if it is still in
        the game boundary and if it has collected the target dot. Returns a
        tuple of (inBoundary, gotTarget)'''
        if not (0 <= target < self.nDots):
            raise ValueError(f"{target} is an invalid target index")

        self.getFrame()
        carContour = self.findCar()
        M = cv.moments(carContour)
        carCentroid = (int(M['m10']/M['m00']),int(M['m01']/M['m00']))
        inBoundary = inContour(self.boundary, carCentroid)
        # Define "collecting a dot" as when the center of the dot is within the
        # contour of the car
        gotTarget = inContour(carContour, self.dots[target][0])

        return (inBoundary, gotTarget)

    def findCar(self):
        '''Find the largest red object in the camera's view, assuming it's the
        car. Return its contour.'''
        # Because red is split between the very bottom and very top of HSV, we
        # have to check two ranges
        redBotObjects = cv.inRange(self.frame, self.redBotLow, self.redBotHigh)
        redTopObjects = cv.inRange(self.frame, self.redTopLow, self.redTopHigh)
        redObjects = cv.bitwise_or(redBotObjects, redTopObjects)

        redContours, _ = cv.findContours(redObjects,
                                        cv.RETR_LIST,
                                        cv.CHAIN_APPROX_SIMPLE)
        return max(redContours, key=lambda c: cv.contourArea(c))

# Utility functions

def inContour(cnt, point):
    '''Takes a contour and a point (x,y) and returns true if that point is
    within the contour.'''
    return cv.pointPolygonTest(cnt, point, False) >= 0