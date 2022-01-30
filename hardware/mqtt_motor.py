import paho.mqtt.client as mqtt
import RPi.GPIO as io
import time
from car import Car

game_over = False
powerup_on = False
time_powerup = 0
old_speed = 20

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
		elif(payload == 'S'):
			pass
		else:
			print('Unknown direction control command')
	elif(str(message.topic) == 'ece180d/team5/speed'):
		if(payload == '+'):
			car.change_Speed(min(car.speed + 10, 100))
		elif(payload == '-'):
			car.change_Speed(max(car.speed - 10, 20))
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
		global powerup_on
		global time_powerup
		global old_speed
		if(payload == 'game over'):
			game_over = True
		elif(payload == 'stop car'):
			car.is_stopped = True
			car.stop_Driving()
		elif(payload == 'start car'):
			car.is_stopped = False
			car.start_Driving()
		elif(payload == 'activate power'):
			powerup_on = True
			time_powerup = time.time()
			#grab the old speed before it's changed
			old_speed = car.speed
			#change to speed to half of the old speed (or 20 minimum)
			car.change_Speed(max(old_speed/2, 20))

client = mqtt.Client()

client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message

#client.connect_async('mqtt.eclipseprojects.io')
client.connect_async('test.mosquitto.org')
client.loop_start()

try:
	while(not(game_over)):
		#if powerup is on, and it's been 3 seconds
		if(powerup_on == True and time.time() - time_powerup >= 3):
			powerup_on = False
			car.change_Speed(old_speed)
			print('Powerup over')
except KeyboardInterrupt:
	io.cleanup()
	client.loop_stop()
	client.disconnect()

io.cleanup()
client.loop_stop()
client.disconnect()

