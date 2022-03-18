# beep boop want to drive
**ECE 180D Team 5**: Derrick Huynh, David Kao, Robert Peralta, Lucas Wolter

## Overview
Beep boop want to drive is a reincarnation of the classic game
[Snake](https://en.wikipedia.org/wiki/Snake_(video_game_genre)), aiming to
bridge the gap between software and hardware in an engaging and entertaining
game. In beep boop want to drive, the user wirelessly steers a hardware car,
which they navigate around a game arena marked out in tape. There are several
dots placed in the arena and the user is directed to random dots in turn. The
user is provided 3 powerups, which they can use to cut the speed of the car in
half for 3 seconds, gaining a new powerup every 5 dots collected. Picking up a
dot increases the speed of the car up to maximum speed after 8 dots. The goal of
the game is to collect as many dots as possible without leaving the arena 3
times.

The game features a hardware, remote-controlled car, gesture recognition
steering, speech recognition game controls, and an overhead camera that uses
computer vision to track the game. A central laptop orchestrates the entire
game, seamlessly blending the disjoint modules together.

## Setup with Provided Hardware

### Game Arena

Take a white poster board and give it a border of black tape, leaving about a
1/2 inch gap between the tape and the edge of the poster board. Cut 4-5 squares
from a piece of black construction paper and tape them to the poster. Affix the
poster to the floor. Position the external camera directly over the poster such
that the entire poster is comfortably in view.

### Car

Make sure the `wpa_supplicant.conf` file is up to date with the wifi network and
password it will be using. Plug the power bank into the RPi and get its IP
address with

```
ping -4 raspberrypi.local
```

Then remotely `ssh` into the RPi and run the script:

```
ssh pi@<IP Address>
conda activate controller
python Team5/hardware/startCar.py
```
You can test if this is successful when running the main controller and having a successful handshake.

### IMU

Make sure the `wpa_supplicant.conf` file is up to date with the wifi network and
password it will be using. Attach the IMU RPi to the computer and log into it
with a serial connection. The necessary script will start automatically.

### Game Controller

Set up the controller environment with the following commands:

```
git clone https://github.com/180D-FW-2021/Team5.git
cd Team5/controller
conda env create -f environment.yml
conda activate controller
```
Then, ensuring that the external webcam is attached to the computer and
functional, find the computer's device handle indices with

```
python start.py --show-devices
```

To determine which of the listed camera indices is the correct one, test them
with commands like

```
python start.py --test-camera --camera <INDEX>
```

After finding the correct camera and microphone indices, start the game with

```
python start.py --camera <INDEX> --microphone <INDEX>
```

---
For full setup instructions and technical details, see the User Manual in
[`docs/README.md`](./docs/README.md).
