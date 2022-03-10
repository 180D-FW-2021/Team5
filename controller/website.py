import requests
import time
import datetime

def publish(username, score, powerups, nTurns, tstart):
    #grab time in game
    tnow = time.time()

    #format into acceptable string
    timestamp = datetime.datetime.fromtimestamp(tnow).strftime('%Y-%m-%d %H:%M:%S')
    hours = int(tnow-tstart) // 3600
    mins = (int(tnow-tstart) % 3600) // 60
    secs = (int(tnow-tstart) % 3600) % 60
    time_ig = '%02d:%02d:%02d' %(hours, mins, secs)

    url = 'https://beepboopw2d.herokuapp.com/api/insert'

    #create json w data
    testdata = {
        "username": username,
        "score": score,
        "powerups_used": powerups,
        "num_turns": nTurns,
        "time_in_game": time_ig,
        "datetimestamp": timestamp,
    }

    x = requests.post(url, json=testdata)
    print(x.text)