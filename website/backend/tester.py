import requests
import time
import datetime

#grab time in game
tstart = time.time()
time.sleep(5)
tnow = time.time()

#format into acceptable string
timestamp = datetime.datetime.fromtimestamp(tnow).strftime('%Y-%m-%d %H:%M:%S')
time_ig = datetime.datetime.fromtimestamp(int(tnow-tstart)).strftime('00:%M:%S')

url = 'https://beepboopw2d.herokuapp.com/api/insert'

#create json w data
testdata = {
    "username": "test57",
    "score": 23,
    "powerups_used": 7,
    "num_turns": 75,
    "time_in_game": time_ig,
    "datetimestamp": timestamp,
}

x = requests.post(url, json=testdata)
print(x.text)   
