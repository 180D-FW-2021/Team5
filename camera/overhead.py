import cv2 as cv
import numpy as np

class Overhead(object):
    def __init__(self, threshMin, threshMax):
        '''Initialize various member variables.'''

        # Colors for drawing
        self.red = [0,0,255]
        self.green = [0,255,0]
        self.blue = [255,0,0]
        self.purple = [255,0,255]
        self.white = [255,255,255]
        self.black = [0,0,0]

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
        self.pFrame = None # Preprocessed version of the current frame
        self.noCar = 0 # Number of frames without a car, for debouncing

    def setup(self):
        '''Parses the game arena, capturing game boundary and dots.'''
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
        if self.car is not None:
            M = cv.moments(self.car)
            carCentroid = (int(M['m10']/M['m00']),int(M['m01']/M['m00']))
            inBoundary = inContour(self.boundary, carCentroid)
            # Define "collecting a dot" as when the center of the dot is within the
            # contour of the car
            gotTarget = inContour(self.car, self.dots[self.target][0])
        else:
            # If we can't find a car, just send safe default values. To make
            # sure we don't penalize the user for one frame where we drop the
            # car, we debounce sending inBoundary = False so we need 20 frames
            # no car in the boundary to declare it outside the boundary
            self.noCar += 1
            if self.noCar == 20:
                self.noCar = 0
                inBoundary = False
            else:
                inBoundary = True
            gotTarget = False

        return (inBoundary, gotTarget)

    def stop(self):
        '''Ensure graceful shutdown by releasing camera.'''
        self.camera.release()

    def getFrame(self):
        '''Gets a frame from the camera, converts it to HSV, and stores it in
        self.frame.'''
        _, self.frame = self.camera.read()
        self.pFrame = self.preprocess()

    def preprocess(self):
        '''Convert image to grayscale and apply a light blur to handle noise. If
        we have a boundary already, fill the area outside the boundary with
        white. This helps with errors down the line, as we don't care about
        data outside the boundary.'''
        gray = cv.cvtColor(self.frame, cv.COLOR_BGR2GRAY)
        blurred = cv.GaussianBlur(gray, (5,5), 0)
        if self.boundary is not None:
            # Inspired by https://stackoverflow.com/questions/37912928/fill-the-outside-of-contours-opencv
            stencil = np.ones(blurred.shape).astype(blurred.dtype) * 255
            stencil = cv.fillPoly(stencil, [self.boundary], 0)
            return cv.bitwise_or(blurred, stencil)
        else:
            return blurred

    def findBoundary(self):
        '''Finds the largest white thing and assumes it is the boundary.'''
        _, whiteThings = cv.threshold(self.pFrame.copy(), 135, 255, cv.THRESH_BINARY)
        # cv.imshow("white things", whiteThings)
        whiteContours, _ = cv.findContours(whiteThings, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        if whiteContours:
            self.boundary = max(whiteContours, key=cv.contourArea)

    def findDots(self):
        '''Finds all black rectangles in the game area. Stores their bounding
        circles in self.dots as ((x,y),radius).'''
        _, blackThings = cv.threshold(self.pFrame.copy(), 70, 255, cv.THRESH_BINARY_INV)
        # cv.imshow("black", blackThings)
        blackContours, _ = cv.findContours(blackThings, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        filteredContours = [c for c in blackContours if inContour(self.boundary, centroid(c)) and nCorners(c) == 4 and cv.contourArea(c) > 100]
        self.dots = [cv.minEnclosingCircle(c) for c in filteredContours]
        self.nDots = len(self.dots)

    def findCar(self):
        '''Find the first black non-rectangle, and assume it's the car. Return
        its contour.'''
        _, blackThings = cv.threshold(self.pFrame.copy(), 70, 255, cv.THRESH_BINARY_INV)
        blackContours, _ = cv.findContours(blackThings, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        maybeCars = [c for c in blackContours if inContour(self.boundary, centroid(c)) and nCorners(c) > 4 and cv.contourArea(c) > 200]
        if maybeCars:
            # TODO: Handle multiple cars
            self.car = maybeCars[0]
        else:
            self.car = None

    def drawFrame(self, target=True, dots=True, car=False, boundary=False):
        '''Draws the requested features onto the current frame, returning the
        modified frame.'''
        # Operate on a copy of the current frame so we don't modify the original
        frame = self.frame.copy()
        if target and self.target is not None:
            # Draw a circle with a larger radius centered on the target dot
            targetCenter, targetRadius = self.dots[self.target]
            targetCenter = tuple(int(x) for x in targetCenter)
            targetRadius = int(targetRadius)
            frame = cv.circle(frame, targetCenter, targetRadius + 5, self.purple, 2)
        if dots and self.dots is not None:
            for center, radius in self.dots:
                center = tuple(int(x) for x in center)
                radius = int(radius)
                frame = cv.circle(frame, center, radius, self.green, 2)
        if car and self.car is not None:
            frame = cv.drawContours(frame, [self.car], 0, self.red, 2)
        if boundary and self.boundary is not None:
            frame = cv.drawContours(frame, [self.boundary], 0, self.blue, 5)

        return frame

# Utility functions

def centroid(cnt):
    '''Computes and returns the centroid point of a given contour.'''
    M = cv.moments(cnt)
    if M['m00']:
        return (int(M['m10']/M['m00']),int(M['m01']/M['m00']))
    else:
        return (0,0)

def inContour(cnt, point):
    '''Takes a contour and a point (x,y) and returns true if that point is
    within the contour.'''
    return cv.pointPolygonTest(cnt, point, False) >= 0

def nCorners(cnt):
    '''Creates an approximation of the given contour and returns the number of
    corners.'''
    perimeter = cv.arcLength(cnt, True)
    approx = cv.approxPolyDP(cnt, 0.035 * perimeter, True)
    return len(approx)

if __name__ == "__main__":
    overhead = Overhead(1000, 3000)
    overhead.setup()

    while True:
        # inBoundary, gotTarget = overhead.loop(0)
        # if not inBoundary:
        #     print("Car out of boundary")
        # if gotTarget:
        #     print("Car got target")
        # frame = overhead.drawFrame(target=False, dots=True, car=True, boundary=True)
        # # Display new frame
        # cv.imshow("overhead", frame)

        overhead.getFrame()

        overhead.findDots()
        overhead.findCar()
        frame = overhead.drawFrame(target=False, dots=True, car=True, boundary=True)
        cv.imshow("pframe", overhead.pFrame)
        cv.imshow("overhead", frame)

    # overhead.getFrame()
    # overhead.findBoundary()
    # frame = overhead.drawFrame(target=False, dots=False, car=False, boundary=True)
    # cv.imshow("frame", overhead.frame)
    # cv.imshow("pframe", overhead.pFrame)
    # cv.imshow("overhead", frame)

    # while True:
    #     print("hello")

        # Stop when ESC is pressed
        k = cv.waitKey(5) & 0xFF
        if k == 27:
            break