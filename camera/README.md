# Computer Vision
Defines the `Overhead` class in `overhead.py`, which wraps all computer vision functionality. `Overhead` provides functions to find the game boundary and dots, as well as track car motion and detect if the car leaves the boundary or picks up a dot.

## `Overhead.__init__(threshold)`
The constructor of the `Overhead` class takes a single parameter, which is the minimum area for a dot. Any contours of the dot color that have an area smaller than this value will be ignored. Generally, this value is on the order of 100s, but it will depend on the final height of the camera above the game arena.

## `Overhead.setup()`
Parses the game arena, finding the game boundary and all dots in the arena. This only accepts dots that have a contour area greater than the threshold given at construction. `setup()` should only be called once the game arena is set up and the camera is steady. A call to `setup()` will set `self.boundary` with the smoothed contour of the boundary, `self.dots` with a list of bounding circles of the dots found, and `self.nDots` with `len(self.dots)`.

## `Overhead.loop(target)`
The main game loop function, which should be called continuously. `loop()` takes a single parameter: the index of the current target dot. The target index must be between 0 inclusive and `Overhead.nDots` exclusive. The target index is not expected to change until the car collects the dot.

Returns the tuple `(inBoundary, gotTarget)`, where `inBoundary` is `True` if the car is still inside the game boundary and `gotTarget` is `True` if the car has collected the target on this frame. If `gotTarget` is `True`, then the target index should change before the next call to `loop()`.