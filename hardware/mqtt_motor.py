import paho.mqtt.client as mqtt
import RPi.GPIO as io
import time
from car import Car

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

def on_message(client, userdata, message):
	global car
	print("Received message:")
	payload = message.payload.decode("utf-8")
	print(payload)
	if(str(message.topic) == 'ece180d/team5/motorControls'):
		if(car.is_stopped == True):
			print('Car is stopped')
		elif(payload == 'L'):
			car.turn_Left()
		elif(payload == 'R'):
			car.turn_Right()
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
			car.stop_Driving()
		elif(payload == 'start car'):
			car.is_stopped = False
			car.start_Driving()

client = mqtt.Client()

client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message

client.connect_async('mqtt.eclipseprojects.io')

client.loop_start()

try:
	while(not(game_over)):
		pass
except KeyboardInterrupt:
	io.cleanup()
	client.loop_stop()
	client.disconnect()

io.cleanup()
client.loop_stop()
client.disconnect()

