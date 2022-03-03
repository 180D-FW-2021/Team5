import requests
import time
import datetime

#grab time in game
tstart = datetime.datetime.now()
time.sleep(1)
tnow = datetime.datetime.now()

print(tnow)

#format into acceptable string
timestamp = tnow.strftime('%Y-%m-%d %H:%M:%S')
print(timestamp)
#time_ig = str(tnow-tstart).strftime('%H:%M:%S')
time_ig = str(tnow-tstart).split('.')[0]
print(time_ig)

# url = 'https://beepboopw2d.herokuapp.com/api/insert'

# #create json w data
# testdata = {
#     "username": "test57",
#     "score": 23,
#     "powerups_used": 7,
#     "num_turns": 75,
#     "time_in_game": time_ig,
#     "datetimestamp": timestamp,
# }

# x = requests.post(url, json=testdata)
# print(x.text)   