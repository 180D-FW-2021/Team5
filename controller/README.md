# Game Controller
Contains the central game controller code. The game controller manages game state and runs the GUI, as well as manages the speech recognition and computer vision modules.

## Speech
The speech recognition module, `speechworker.py` is adapted from the Porucupine demo found in `Team5/speech`. The base paths of the models need to be specified and should be updated monthly because they expire. The access key from Picovoice Console also needs to be provided.

The class inherits from a [PyQt Qthread](https://doc.qt.io/qtforpython/PySide6/QtCore/QThread.html) object to ensure compatibility with the GUI (so it doesn't freeze while listening for keywords). 

## GUI
The GUI uses PyQT5. Install using 

```
pip install PyQt5
```

`cameraworker.py` and `speechworker.py` have been adapted to emit pyqtSignals which don't block threads. This allows them to collect and pass information to the GUI without freezing or crashing the GUI. These signals are passed into "slots", which are similar to event handlers natively attached to GUI elements.

The basic GUI is split into two halves. The left half is the camera view, augmented with callouts of the arena boundary, the targets, the current objective, and the location of the car. The right half contains the start button and five text labels. The start button allows the controller to scan the arena and prepare the camera to track the game. The five text labels are, in order: the current game state (running, paused); the player's score, number of lives, number of powerups, and the tooltip. The tooltip changes dynamically based on the current game state. Several of the labels also flash red when appropriate.

![image](https://user-images.githubusercontent.com/20711319/146618508-3b1a1ae5-758b-41c1-85a7-5e993c7acf0e.png)
