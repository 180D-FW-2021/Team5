import argparse
from contextlib import contextmanager
import os
import time

import cv2 as cv
from pvrecorder import PvRecorder
from PyQt5.QtMultimedia import QCameraInfo

from controller import run
from mqtt import HandshakeMqtt

@contextmanager
def suppressStderr():
    '''Context manager to suppress stderr, silencing harmless openCV warnings.
    Based on https://stackoverflow.com/questions/11130156/suppress-stdout-stderr-print-from-python-functions'''
    try:
        # Get a devnull fd and save the real stderr fd
        nullFd = os.open(os.devnull, os.O_RDWR)
        errFd = os.dup(2)
        # Replace stderr with devnull
        os.dup2(nullFd, 2)
        yield
    finally:
        # Restore stderr
        os.dup2(errFd, 2)
        # Close extra fds
        for fd in (nullFd, errFd):
            os.close(fd)

def showDevices():
    '''Prints out camera and microphone handle indices and names.'''

    # Print cameras and their indices
    print('Camera names:')
    cameras = QCameraInfo.availableCameras()
    cameras = [c.description() for c in cameras]
    print(', '.join(cameras))

    with suppressStderr():
        validIndices = []
        for i in range(10):
            cam = cv.VideoCapture(i)
            if cam.isOpened():
                validIndices.append(str(i))
            cam.release()
    print('Camera indices:')
    print(', '.join(validIndices))
    print('The camera names ARE NOT ordered by index! You will have to try a few indices to find the right one.')

    # Print microphones and their indices
    print('\nMicrophones:')
    mics = PvRecorder.get_audio_devices()
    for i,mic in enumerate(mics):
        print(f'{i} {mic}')
    print('These indices ARE correctly matched up.')

def parseArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('--show-devices', action='store_true', dest='devices',
        help='Show all connected cameras and microphones and exit.')
    parser.add_argument('--test-camera', action='store_true', dest='test',
        help='Show the video from the current camera index. Must be used with --camera.')
    parser.add_argument('-c', '--camera', default=-1, type=int, metavar='INDEX',
        help='Index of camera handle to use.')
    parser.add_argument('-m', '--microphone', default=-1, type=int, metavar='INDEX',
        help='Index of microphone handle to use.')
    return parser.parse_args()

def main():
    args = parseArgs()

    if args.devices:
        showDevices()
    elif args.test:
        if args.camera < 0:
            print('--test-camera must be used with a valid value for --camera.')
            exit(1)
        cam = cv.VideoCapture(args.camera)
        print('Press ESC to exit.')
        while True:
            _, frame = cam.read()
            cv.imshow(f'Index {args.camera}', frame)

            k = cv.waitKey(5) & 0xFF
            if k == 27:
                break
        with suppressStderr():
            cam.release()       
    elif args.camera < 0 or args.microphone < 0:
        print('If starting the game, must give values for both --camera and --microphone.')
        exit(1)
    else:
        handshake = HandshakeMqtt()
        last = 0
        n = 1
        while not handshake.imu and not handshake.car:
            if not handshake.imu and not handshake.car:
                devices = 'IMU and car'
            elif not handshake.imu:
                devices = 'IMU'
            elif not handshake.car:
                devices = 'car'

            # Send handshake and update display every half second
            if time.time() - last > 0.5:
                handshake.sendHandshake()
                last = time.time()
                n = 1 if n == 3 else n + 1
                print('Waiting for ' + devices + '.'*n + ' '*20, end='\r')
            
        print('Starting game' + ' '*20)
        handshake.stop()
        run(args.camera, args.microphone)

if __name__ == '__main__':
    main()