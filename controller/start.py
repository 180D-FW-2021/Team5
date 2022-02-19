import argparse
from contextlib import contextmanager
import os

import cv2 as cv
from pvrecorder import PvRecorder
from PyQt5.QtMultimedia import QCameraInfo

from controller import run

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
    parser.add_argument('-c', '--camera', default=-1, type=int, metavar='INDEX',
        help='Index of camera handle to use.')
    parser.add_argument('-m', '--microphone', default=-1, type=int, metavar='INDEX',
        help='Index of microphone handle to use.')
    return parser.parse_args()

def main():
    args = parseArgs()

    if args.devices:
        showDevices()
        exit(0)
    elif args.camera == -1 or args.microphone == -1:
        print('If not using --show-devices, must give values for --camera and --microphone.')
        exit(1)
    else:
        run()
        # cam = cv.VideoCapture(args.camera)
        # while True:
        #     _, frame = cam.read()
        #     cv.imshow('cam', frame)

        #     k = cv.waitKey(5) & 0xFF
        #     if k == 27:
        #         break

if __name__ == '__main__':
    main()