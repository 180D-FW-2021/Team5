import requests
import time
import datetime

def publish(username, score, powerups, turns, tstart):
    #grab time in game
    tnow = time.time()

    #format into acceptable string
    timestamp = datetime.datetime.fromtimestamp(tnow).strftime('%Y-%m-%d %H:%M:%S')
    time_ig = datetime.datetime.fromtimestamp(int(tnow-tstart)).strftime('&H:%M:%S')

    url = 'https://beepboopw2d.herokuapp.com/api/insert'

    #create json w data
    testdata = {
        "username": username,
        "score": score,
        "powerups_used": powerups,
        "num_turns": turns,
        "time_in_game": time_ig,
        "datetimestamp": timestamp,
    }

    x = requests.post(url, json=testdata)
    print(x.text)

