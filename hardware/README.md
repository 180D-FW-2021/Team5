# Hardware
Code related to controlling and running the car

## `Car.__init__(in1, in2, in3, in4, enL, enR)`
The constructor of the `Car` class takes 6 parameters for the 4 input pins, and the 2 enable pins. The input pins control the direction of the motor and the enable pins control the speed.

Note: The enable pins MUST be PWM. On RPi, PWM are pins 12,13,18,19.

## `MQTT Commands`
### topic = `ece180d/team5/motorControls`
payload:
'L' - turns car left

'R' - turns car right

it works by running the motors in a different direction in a while loop for left(right)_turn_length seconds. This is a WIP as the length needs to be a function of the speed
after running in different direction, it then outputs the in pins to drive straight.

### topic = `ece180d/team5/speed`
the speed can only be between [20, 100]
payload:
'+' - increases the speed by 10%

'-' - decreases the speed by 10%

'#' (20 <= # <= 100) - sets custom speed at #%

### topic = `ece180d/team5/game`
Controls game functions
payload:
'game over' - stops the game and ends the script

'stop car' - stops the car and disables inputs (L/R)

'start car' - restarts car at previous speed

'activate power' - activates powerup that sets the speed to half the current speed. After 3 seconds, it returns to the old speed.
