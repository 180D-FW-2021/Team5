import argparse
from PyQt5.QtMultimedia import QCameraInfo

from controller import run
from pvrecorder import PvRecorder

def showDevices():
    '''Prints out camera and microphone handle indices and names.'''

    # Print cameras and their indices
    print('Cameras:')
    cameras = QCameraInfo.availableCameras()
    for i,camera in enumerate(cameras):
        print(f'{i}. {camera.description()}')

    # Print microphones and their indices
    print('\nMicrophones:')
    mics = PvRecorder.get_audio_devices()
    for i,mic in enumerate(mics):
        print(f'{i}. {mic}')

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

if __name__ == '__main__':
    main()