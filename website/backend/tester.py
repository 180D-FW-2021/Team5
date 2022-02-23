import requests
import time
import datetime

tstart = time.time()
time.sleep(5)
tnow = time.time()
timestamp = datetime.datetime.fromtimestamp(tnow).strftime('%Y-%m-%d %H:%M:%S')
time_ig = datetime.datetime.fromtimestamp(int(tnow-tstart)).strftime('00:%M:%S')

testing = True

if(testing):
    url = 'http://localhost:3001/api/insert'
else:
    url = 'https://beepboopw2d.herokuapp.com/api/insert'

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