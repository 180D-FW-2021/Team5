# beep boop want to drive
**ECE 180D Team 5**: Derrick Huynh, David Kao, Robert Peralta, Lucas Wolter

## Overview
Beep boop want to drive is a reincarnation of the classic game [Snake](https://en.wikipedia.org/wiki/Snake_(video_game_genre)), aiming to bridge the gap between software and hardware in an engaging and entertaining game. In beep boop want to drive, the user wirelessly steers a hardware car, which they navigate around a game arena marked out in tape. There are several dots placed in the arena and the user is directed to random dots in turn. The user is provided 3 powerups, which they can use to cut the speed of the car in half for 3 seconds. Picking up a dot increases the speed of the car up to maximum speed after 8 dots. The goal of the game is to collect as many dots as possible without leaving the arena 3 times.

The game features a hardware, remote-controlled car, gesture recognition steering, speech recognition game controls, and an overhead camera that uses computer vision to track the game. A central laptop orchestrates the entire game, seamlessly blending the disjoint modules together.

## Setup
The game has 3 computers which all require different software running on them: the RPi with the IMU, the RPi on the car, and the controlling laptop. In total, you will need the following:

* Laptop (1)
* External webcam or smartphone (1)
  * If using a phone, you will need a camera mount to hold the phone over the game arena
* RaspberryPi Zero WH (2)
* BerryIMUv3 (1)
* 9V Battery
* 5V battery powerbank
* Hardware car
* White poster board
* Black paper
* Miscellaneous wires and connectors (Recommended to have ~8 Female-Male)

Note that the hardware car is not described in detail here. Currently we have no schematic of the car to share, but the car is based on an [L293 H-bridge](https://www.adafruit.com/product/807) and 2 9V DC motors, and an industrious user could investigate the code in the `hardware` directory to determine pin assignments on the RPi. Refer to the following info on how the H–Bridge works: [Direction Truth Table](https://drive.google.com/file/d/1n0UCoyRyvaSpgobGnBY8AHq8t6nLdRKh/view?usp=sharing), [H-Bridge Pinout](https://drive.google.com/file/d/1lcsleWE-I3sc4Y-wqP7EvscM3ZZQUWd-/view?usp=sharing).

### Arena
The arena has 3 main components: the boundary, the dots, and the car. These components are differentiated by their shape and color. The boundary will always be the outline of the white poster board, the dots are represented by solid black rectangles/squares, and the car is marked with a black circle. For the arena to be valid, there must be a white poster board with at least two dots and the car fully within its bounds.

The arena is overseen by the external camera. This can be a standard webcam or a smartphone running [DroidCam](https://www.dev47apps.com/). Importantly, the code assumes this camera is a secondary webcam for the controller laptop. If this camera is the primary webcam, change [this line](https://github.com/180D-FW-2021/Team5/blob/main/camera/overhead.py#L41) in `camera/overhead.py` to

    self.camera = cv.VideoCapture(0)

### Gesture RPi
These setup instructions are adapted from lab 4.
To setup the IMU controller, first connect the BerryIMU to the Raspberry Pi as shown:
![alt text](https://github.com/180D-FW-2021/Team5/blob/fda2e14a4b80961ee594399cf037b4bf1a368d94/gesture/Images/hw-setup.PNG)

Next, enter the following commands into the Raspberry Pi command line to install the necessary components:

    sudo apt-get update
    sudo apt-get upgrade
    conda upgrade conda
    conda update conda
    pip install --upgrade pip
    sudo apt-get install git i2c-tools libi2c-dev
    conda install -c conda-forge smbus2

Try opening the blacklist file `/etc/modprobe.d/raspi-blacklist.conf`. If the file contains the line `blacklist i2c-bcm2708`, place a '#' in front to comment it out. If the file is empty or can't be opened then continue.

Add the following lines into `/etc/modules`:

    i2c-dev
    i2c-bcm2708

Add the following lines into `/boot/config.txt`:

    dtparam=i2c_arm=on
    dtparam=i2c1=on

Reboot the RPi, then enter in the command line `sudo i2cdetect -y 1`. The following should be displayed:
![alt text](https://github.com/180D-FW-2021/Team5/blob/fda2e14a4b80961ee594399cf037b4bf1a368d94/gesture/Images/i2cdetect.PNG)

Next, run `git clone https://github.com/180D-FW-2021/Team5.git` to clone the repository. Run the following commands to navigate to and run the IMU controller code. Always run IMU controller code before running Car RPi code. Press `Ctrl+C` to stop running IMU controller code.

    cd Team5/gesture/BerryIMU/python-BerryIMU-gyro-accel-compass-filters
    python berryIMU.py

### Car RPi
The only set up needed for the Car RPi is to connect to the internet by modifying the `wpa_supplicant.conf` file. Once connected, run `ifconfig` to obtain the IP address under the `WLAN0: inet`. Then enter the settings to enable remote ssh.

Then connect the RPi to the powerbank, then remote ssh and clone the repo.

    ssh pi@<ip address>
    git clone https://github.com/180D-FW-2021/Team5.git
    
Then go to the `Team5/hardware` folder. You will need to modify the file to change any pin assignments and MQTT topics as needed. Note that `enL` and `enR` MUST be PWM pins (pins 12,13,18,19)

    nano mqtt_motor.py
        in1 = ...
        in2 = ...
        etc.
    
The virtual environment provided in `controller/environment.yml` has all necessary packages to run the car software. Follow the steps in the Controller Laptop section to create the same environment on the Car RPi. Then activate the environment and run the main code.
    
    conda activate controller
    python mqtt_motor.py

Since the `controller` environment contains many large packages that the car will never use, you can also create a simpler environment, including only the `paho-mqtt` package.

    conda create -n <envname> -c conda-forge paho-mqtt
    conda activate <envname>
    python mqtt_motor.py

1. If your car responds to messages that your controller did not send, make sure that you are not responding to other messages on the same mqtt topic. If this occurs, please change the topic on all MQTT programs. 
2. Note: you can modify the turning length of the car by editing the car.py file's left_turn_length and right_turn_length.
3. If you suddenly lose connection to the car, it is possible that the car left the range of the remote ssh. In this case, you will need to reconnect to the car and rerun the program. In the case that the motors are still running, press `Ctrl+C` to abort the program (this will cause the car to stop the motors) and you may restart the game as normal.

    
### Controller Laptop
(*This laptop needs a microphone in order to process speech inputs.*)

Clone the repository.

    git clone https://github.com/180D-FW-2021/Team5.git

In an Anaconda shell, change the directory to `Team5/controller` and create a new environment with the YAML file.

    cd Team5/controller
    conda env create -f environment.yml

Activate the environment and run `controller.py`.

    conda activate controller
    python controller.py

After a moment, the GUI will appear with an "Arena Ready" button. Click the button only once the arena is properly set up to start the game.

The GUI will display information about the game parts it has parsed. The boundary will be outlined in blue, the dots will have green circles around them, and the car will be outlined in red. The target dot, the next dot the player should aim to get, will have an extra purple circle around it.

Running `python controller.py` may fail with an error about a license expiring. Because this project uses the free version of [Porcupine](https://picovoice.ai/platform/porcupine/), the speech recognition models eventually expire. If a user so desires, they could train a new model of the same keywords and place the model in `speech/porcupine_models`. The user would also have to change the file paths in [`controller/speechworker.py`](https://github.com/180D-FW-2021/Team5/blob/main/controller/speechworker.py#L15).
