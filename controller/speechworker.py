from PyQt5.QtCore import QThread, pyqtSignal
import numpy as np
import pvporcupine
from pvrecorder import PvRecorder
import os
import platform

class SpeechWorker(QThread):
    '''Thread to handle speech recognition.'''
    keywordDetected = pyqtSignal(str)

    def __init__(self, index):
        super().__init__()
        # Store microphone device index on construction
        self.index = index
        self.active = False

    def run(self):
        self.active = True

        modelBasePath = "../speech/porcupine_models/"

        # Load platform-specific models
        if platform.system() == "Windows":
            modelFiles = ["continue_en_windows_v2_1_0.ppn",
                      "game-pause_en_windows_v2_1_0.ppn",
                      "activate-power_en_windows_v2_1_0.ppn"]
        elif platform.system() == "Darwin":
            modelFiles = ["Continue_en_mac_v2_1_0.ppn",
                        "Game-Pause_en_mac_v2_1_0.ppn",
                        "Activate-Power_en_mac_v2_1_0.ppn"]
        else:
            raise RuntimeError("Running on unsupported platform. Currently only Windows and MacOS are supported.")
        keywordPaths = [modelBasePath + f for f in modelFiles]
        self.getKeywords(keywordPaths)

        self.sensitivities = [0.5] * len(keywordPaths)

        self.porcupine = pvporcupine.create(
            library_path=pvporcupine.LIBRARY_PATH,
            model_path=pvporcupine.MODEL_PATH,
            keyword_paths=keywordPaths,
            sensitivities=self.sensitivities,
            access_key="OoBm7DUZ0/3C9mx28fclJIzBBRBWKiPftaZIDAVc0QiAH7QPBYVhCg==")
        self.recorder = PvRecorder(device_index=self.index,
            frame_length=self.porcupine.frame_length)
        print(f'Using device: {self.recorder.selected_device}')
        self.recorder.start()

        print('Listening {')
        for keyword, sensitivity in zip(self.keywords, self.sensitivities):
            print('  %s (%.2f)' % (keyword, sensitivity))
        print('}')

        while self.active:
            pcm = self.recorder.read()
            result = self.porcupine.process(pcm)
            if result >= 0:
                print("Detected %s" % self.keywords[result])
                self.keywordDetected.emit(self.keywords[result].strip())

    def stop(self):
        self.active = False
        if self.porcupine:
            self.porcupine.delete()
        if self.recorder:
            self.recorder.delete()
        self.quit()

    def getKeywords(self, keywordPaths):
        '''Given the list of keyword paths, adds a list of the keywords
        themselves to self.keywords. Taken directly from Porcupine demo code.'''
        self.keywords = []
        for x in keywordPaths:
            keyword_phrase_part = os.path.basename(x).replace('.ppn', '').split('_')
            if len(keyword_phrase_part) > 6:
                self.keywords.append(' '.join(keyword_phrase_part[0:-6]))
            else:
                self.keywords.append(keyword_phrase_part[0])
