# Speech Recognition
Code related to detecting and handling keyword recognition

## Porcupine Keyword Detection
Uses the Porcupine demo developed by Picovoice (Python) found here: https://github.com/Picovoice/porcupine/tree/master/demo/python

Code adapted from porcupine_demo_mic.py, found in the above repo. Relevant parts of documentation included below.

## Setup
To install on your system, use the command `sudo pip3 install pvporcupinedemo`.

## AccessKey
You need to make an account on the [Picovoice Console] (https://picovoice.ai/console/) first. After you log in, find your access key on the [top bar] (https://console.picovoice.ai/access_key). 

## Setup demo
The controller doesn't expose the demo code, but to run the demo file, porcupine_demo_mic.py:

```
porcupine_demo_mic --access_key ${ACCESS_KEY} --keywords picovoice
```

Replace ${ACCESS_KEY} with your access key. Using the --keywords option will recognize keywords from the Porcupine default library. To select which words to choose, just list them separated by a space after the "--keywords" option. To see the default words, use:

```
porcupine_demo_mic --help
```

## Custom keywords
Our system uses custom keywords which are trained using the Picovoice Console. To train keyword models, go to Porcupine and train custom wake words. You can train three models every 30 days for free. Our wake words are "activate power", "game pause", and "continue". The platform is for Windows (x86-64) and the version is for Porcupine v2.0.0.

After it's trained, download the file (.zip). Extract the .ppn file inside.

To recognize the keywords, use:

```
porcupine_demo_mic --access_key ${ACCESS_KEY} --keyword_paths ${KEYWORD_PATH_ONE} ${KEYWORD_PATH_TWO}
```

## Speech Implementation
More information on the speech implementation can be found in `Team5/controller`.

## Python Speech Recognition Library
To use the speech recognition library that was tested before, you need to install the [speech_recognition] (https://github.com/Uberi/speech_recognition) library.

To do that, first run

```
pip install SpeechRecognition
```

Then, you need PyAudio to use the mic. Documentation says to use 

```
pip install pyaudio
```

but that didn't work for me. I used

```
pip install pipwin
pipwin install pyaudio
```

and that did the trick. 
To install PocketSphinx, run
```
python -m pip install --upgrade pip setuptools wheel
pip install --upgrade pocketsphinx
```

Google Speech Recognition doesn't require setup if you're not using the API. Run `speech_recognition/microphone_recognition.py` to try.