from PyQt5.QtCore import QThread, pyqtSignal
import numpy as np
import pvporcupine
from pvrecorder import PvRecorder
import os

class SpeechWorker(QThread):
    '''Thread to handle speech recognition.'''
    keywordDetected = pyqtSignal(str)

    def run(self):
        self.active = True

        modelBasePath = "../speech/porcupine_models/"
        modelFiles = [#"continue__en_windows_2021-12-01-utc_v1_9_0.ppn",
                      #"game-pause__en_windows_2021-12-01-utc_v1_9_0.ppn",
                      "activate-power__en_windows_2021-12-18-utc_v1_9_0.ppn"]
        keywordPaths = [modelBasePath + f for f in modelFiles]
        self.getKeywords(keywordPaths)

        self.sensitivities = [0.5] * len(keywordPaths)

        self.porcupine = pvporcupine.create(
            library_path=pvporcupine.LIBRARY_PATH,
            model_path=pvporcupine.MODEL_PATH,
            keyword_paths=keywordPaths,
            sensitivities=self.sensitivities)
        self.recorder = PvRecorder(device_index=0,
            frame_length=self.porcupine.frame_length)

        print('Listening {')
        for keyword, sensitivity in zip(self.keywords, self.sensitivities):
            print('  %s (%.2f)' % (keyword, sensitivity))
        print('}')

        while self.active:
            pcm = self.recorder.read()
            result = self.porcupine.process(pcm)
            if result >= 0:
                print("Detected %s" % self.keywords[result])
                self.keywordDetected.emit(self.keywords[result])

    def stop(self):
        self.active = False
        self.porcupine.delete()
        self.recorder.delete()

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
