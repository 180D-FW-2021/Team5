import cv2 as cv
import numpy as np

class Overhead(object):
    def __init__(self, threshMin, threshMax):
        '''Initialize various member variables.'''

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
        self.greenLow = np.uint8([25,50,50]) # Actually for yellow post-its
        self.greenHigh = np.uint8([45,255,255])
        self.blueLow = np.uint8([80,20,30])
        self.blueHigh = np.uint8([170,255,255])

        # Other variables
        self.boundary = None # Boundary contour
        self.dots = None # List of dots in the arena
        self.nDots = -1 # Number of dots parsed in the arena
        self.car = None # Contour of the car
        self.target = -1 # Index of target dot in dots list
        self.threshMin = threshMin # Min area for parsing dots
        self.threshMax = threshMax # Max area for parsing dots
        self.camera = cv.VideoCapture(1) # DroidCam handle
        self.frame = None # Current frame being processed

    def setup(self):
        '''Parses the game arena, capturing game boundary and dots. Assumes
        boundary is blue and dots are green.'''
        # Keep taking frames until we've found a boundary and at least one dot
        while (self.boundary is None) or (not self.dots):
            self.getFrame()
            if (self.frame is not None) and (self.frame.any()):
                self.findBoundary()
                self.findDots()

                # k = cv.waitKey(5) & 0xFF
                # if k == 27:
                #     break

    def loop(self, target):
        '''Main function to be called each game loop. Takes in the index of
        current target in dots list. Finds the car and sees if it is still in
        the game boundary and if it has collected the target dot. Returns a
        tuple of (inBoundary, gotTarget)'''
        self.target = target
        if not (0 <= self.target < self.nDots):
            raise ValueError(f"{self.target} is an invalid target index")

        self.getFrame()
        self.findCar()
        M = cv.moments(self.car)
        carCentroid = (int(M['m10']/M['m00']),int(M['m01']/M['m00']))
        inBoundary = inContour(self.boundary, carCentroid)
        # Define "collecting a dot" as when the center of the dot is within the
        # contour of the car
        gotTarget = inContour(self.car, self.dots[self.target][0])

        return (inBoundary, gotTarget)

    def stop(self):
        '''Ensure graceful shutdown by releasing camera.'''
        self.camera.release()

    def getFrame(self):
        '''Gets a frame from the camera, converts it to HSV, and stores it in
        self.frame.'''
        _, frame = self.camera.read()
        self.frame = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

    def findBoundary(self):
        '''Finds the largest blue object and assumes it is the boundary. Creates
        an approximation of the contour to smooth any details, and stores the
        approximation in self.boundary.'''
        blueObjects = cv.inRange(self.frame, self.blueLow, self.blueHigh)
        # cv.imshow("maybe boundary", blueObjects)
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

    def findDots(self):
        '''Finds all green objects with contour area larger than self.threshold.
        Stores their bounding circles in self.dots as ((x,y),radius).'''
        greenObjects = cv.inRange(self.frame, self.greenLow, self.greenHigh)
        # cv.imshow("maybe dots", greenObjects)
        greenContours, _ = cv.findContours(greenObjects,
                                        cv.RETR_LIST,
                                        cv.CHAIN_APPROX_SIMPLE)
        filteredContours = filter(lambda c: self.threshMax > cv.contourArea(c) > self.threshMin, greenContours)
        self.dots = [cv.minEnclosingCircle(c) for c in filteredContours]
        self.nDots = len(self.dots)

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
        self.car = max(redContours, key=lambda c: cv.contourArea(c))

    def drawFrame(self, target=True, dots=True, car=False, boundary=False):
        '''Draws the requested features onto the current frame, converting it
        back to RGB and returning the modified frame.'''
        # Operate on a copy of the current frame so we don't modify the original
        frame = self.frame.copy()
        if target:
            # Draw a circle with a larger radius centered on the target dot
            targetCenter, targetRadius = self.dots[self.target]
            targetCenter = tuple(int(x) for x in targetCenter)
            targetRadius = int(targetRadius)
            frame = cv.circle(frame, targetCenter, targetRadius + 5, self.purple, 2)
        if dots:
            for center, radius in self.dots:
                center = tuple(int(x) for x in center)
                radius = int(radius)
                frame = cv.circle(frame, center, radius, self.green, -1)
        if car:
            frame = cv.drawContours(frame, [self.car], 0, self.red, 2)
        if boundary:
            frame = cv.drawContours(frame, [self.boundary], 0, self.blue, 5)

        return cv.cvtColor(frame, cv.COLOR_HSV2BGR)

# Utility functions

def inContour(cnt, point):
    '''Takes a contour and a point (x,y) and returns true if that point is
    within the contour.'''
    return cv.pointPolygonTest(cnt, point, False) >= 0

if __name__ == "__main__":
    overhead = Overhead(500, 2000)
    overhead.setup()
    while True:
        inBoundary, gotTarget = overhead.loop(0)
        if not inBoundary:
            print("Car out of boundary")
        if gotTarget:
            print("Car got target")
        frame = overhead.drawFrame(target=True, dots=True, car=True, boundary=True)
        # Display new frame
        cv.imshow("overhead", frame)

        # Stop when ESC is pressed
        k = cv.waitKey(5) & 0xFF
        if k == 27:
            break