import paho.mqtt.client as mqtt
import io
import time
from car import Car

#these lengths are in seconds
left_turn_length = 0.4
right_turn_length = 0.5
speed = 20
game_over = False

#set up motor pins and en pins. 12,13,18,19 are PWM. We use PWM to control the motor speed on enR and enL.
in1 = 17
in2 = 27
in3 = 23
in4 = 24
enR = 13
enL = 19

car = Car(in1, in2, in3, in4, enR, enL)

def on_connect(client, userdata, flags, rc):
	print("Connection returned result: "+str(rc))

	client.subscribe("ece180d/team5/#", qos=1)

def on_disconnect(client, userdata, rc):
	if rc != 0:
		print("Unexpected Disconnect")
	else:
		print("Expected Disconnect")

def on_message(car, client, userdata, message):
	print("Received message:")
	payload = message.payload.decode("utf-8")
	print(payload)
	if(str(message.topic) == 'ece180d/team5/motorControls'):
		if(payload == 'L' and not(car.is_stopped)):
			car.turn_left()
		elif(payload == 'R' and not(car.is_stopped)):
			car.turn_right()
		else:
			print('Unknown direction control command')
	elif(str(message.topic) == 'ece180d/team5/speed'):
		if(payload == '+' and car.speed <= 90):
			car.change_Speed(car.speed + 10)
		elif(payload == '-' and car.speed >= 20):
			car.change_Speed(car.speed - 10)
		else:
			try:
				temp = int(payload)
				if(temp >= 20 and temp <= 100):
					car.change_Speed(temp)
				else:
					print('invalid input speed. It must be between [20, 100]')
			except:
				print('Unknown speed command')
	elif(str(message.topic) == 'ece180d/team5/game'):
		global game_over
		if(payload == 'game over'):
			game_over = True
		elif(payload == 'stop car'):
			car.is_stopped = True
			car.stop_driving()
		elif(payload == 'start car'):
			car.is_stopped = False

client = mqtt.Client()

client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message(car)

client.connect_async('mqtt.eclipseprojects.io')

client.loop_start()

while(not(game_over)):
	try:
		pass
	except KeyboardInterrupt:
		io.cleanup()
		client.loop_stop()
		client.disconnect()

io.cleanup()
client.loop_stop()
client.disconnect()

