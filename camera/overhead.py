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
        self.yellowLow = np.uint8([25,50,50])
        self.yellowHigh = np.uint8([60,255,255])
        self.blueLow = np.uint8([80,20,30])
        self.blueHigh = np.uint8([125,255,255])

        # Color bounds to use
        self.carLow = (self.redBotLow, self.redTopLow)
        self.carHigh = (self.redBotHigh, self.redTopHigh)
        self.boundaryLow = self.blueLow
        self.boundaryHigh = self.blueHigh
        self.dotLow = self.yellowLow
        self.dotHigh = self.yellowHigh

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
        # Keep taking frames until we've found a boundary and at least two dots
        while (self.boundary is None) or (len(self.dots) < 2):
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
        if self.car:
            M = cv.moments(self.car)
            carCentroid = (int(M['m10']/M['m00']),int(M['m01']/M['m00']))
            inBoundary = inContour(self.boundary, carCentroid)
            # Define "collecting a dot" as when the center of the dot is within the
            # contour of the car
            gotTarget = inContour(self.car, self.dots[self.target][0])
        else:
            # If we can't find a car, just send safe default values
            inBoundary = False
            gotTarget = False

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
        maybeBoundary = cv.inRange(self.frame, self.boundaryLow, self.boundaryHigh)
        # cv.imshow("maybe boundary", maybeBoundary)
        boundaryContours, _ = cv.findContours(maybeBoundary,
                                    cv.RETR_LIST,
                                    cv.CHAIN_APPROX_NONE)
        if boundaryContours:
            # Take the largest contour and make an approximation of it to
            # smooth the outline
            # TODO: Change to find inner edge of boundary
            boundary = max(boundaryContours, key=cv.contourArea)
            epsilon = 0.01 * cv.arcLength(boundary, True)
            outline = cv.approxPolyDP(boundary, epsilon, True)
            self.boundary = outline

    def findDots(self):
        '''Finds all green objects with contour area larger than self.threshold.
        Stores their bounding circles in self.dots as ((x,y),radius).'''
        maybeDots = cv.inRange(self.frame, self.dotLow, self.dotHigh)
        # cv.imshow("maybe dots", maybeDots)
        dotContours, _ = cv.findContours(maybeDots,
                                        cv.RETR_LIST,
                                        cv.CHAIN_APPROX_SIMPLE)
        # print([cv.contourArea(c) for c in dotContours])
        filteredContours = filter(lambda c: self.threshMax > cv.contourArea(c) > self.threshMin, dotContours)
        self.dots = [cv.minEnclosingCircle(c) for c in filteredContours]
        self.nDots = len(self.dots)

    def findCar(self):
        '''Find the largest red object in the camera's view, assuming it's the
        car. Return its contour.'''
        # Because red is split between the very bottom and very top of HSV, we
        # have to check two ranges
        carBotObjects = cv.inRange(self.frame, self.carLow[0], self.carHigh[0])
        carTopObjects = cv.inRange(self.frame, self.carLow[1], self.carHigh[1])
        maybeCars = cv.bitwise_or(carBotObjects, carTopObjects)

        carContours, _ = cv.findContours(maybeCars,
                                        cv.RETR_LIST,
                                        cv.CHAIN_APPROX_SIMPLE)
        if carContours:
            self.car = max(carContours, key=lambda c: cv.contourArea(c))
        else:
            self.car = None

    def drawFrame(self, target=True, dots=True, car=False, boundary=False):
        '''Draws the requested features onto the current frame, converting it
        back to RGB and returning the modified frame.'''
        # Operate on a copy of the current frame so we don't modify the original
        frame = self.frame.copy()
        if target and self.target is not None:
            # Draw a circle with a larger radius centered on the target dot
            targetCenter, targetRadius = self.dots[self.target]
            targetCenter = tuple(int(x) for x in targetCenter)
            targetRadius = int(targetRadius)
            frame = cv.circle(frame, targetCenter, targetRadius + 5, self.purple, 2)
        if dots and self.dots:
            for center, radius in self.dots:
                center = tuple(int(x) for x in center)
                radius = int(radius)
                frame = cv.circle(frame, center, radius, self.green, -1)
        if car and self.car:
            frame = cv.drawContours(frame, [self.car], 0, self.red, 2)
        if boundary and self.boundary:
            frame = cv.drawContours(frame, [self.boundary], 0, self.blue, 5)

        return cv.cvtColor(frame, cv.COLOR_HSV2BGR)

# Utility functions

def inContour(cnt, point):
    '''Takes a contour and a point (x,y) and returns true if that point is
    within the contour.'''
    return cv.pointPolygonTest(cnt, point, False) >= 0

if __name__ == "__main__":
    overhead = Overhead(1000, 3000)
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