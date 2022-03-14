import cv2 as cv
from overhead import Overhead
from random import randint

def main():
    '''An example of using the Overhead class.'''
    overhead = Overhead(200)
    # Ideally, this script would wait for user confirmation that the arena and
    # camera are set up before calling setup()
    overhead.setup()

    target = newTarget(overhead.nDots, -1)
    while True:
        inBoundary, gotTarget = overhead.loop(target)
        if not inBoundary:
            # Lose a life and stop the car or some other penalty
            pass
        if gotTarget:
            target = newTarget(overhead.nDots, target)
            # Award points, increase car speed, etc.

        frame = overhead.drawFrame()
        cv.imshow("Overhead", frame)

        # Stop when ESC is pressed
        k = cv.waitKey(5) & 0xFF
        if k == 27:
            break
    
    cv.destroyAllWindows()

def newTarget(nDots, lastTarget):
    '''Returns a new target dot index. Makes sure that the same dot is not
    chosen twice.'''
    target = randint(0, nDots - 1)
    while target == lastTarget:
        target = randint(0, nDots - 1)
    return target

if __name__ == "__main__":
    main()