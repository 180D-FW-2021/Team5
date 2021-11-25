import paho.mqtt.client as mqtt
import RPi.GPIO as io
import time


left_turn_length = 0.4
right_turn_length = 0.5
speed = 20
is_stopped = False

def on_connect(client, userdata, flags, rc):
	print("Connection returned result: "+str(rc))

	client.subscribe("ece180d/team5/#", qos=1)

def on_disconnect(client, userdata, rc):
	if rc != 0:
		print("Unexpected Disconnect")
	else:
		print("Expected Disconnect")

def on_message(client, userdata, message):
	print("Received message:")
	if(str(message.topic) == 'ece180d/team5/motorControls'):
		payload = message.payload.decode("utf-8")
		print(payload)
		if(payload == 'L' and not(is_stopped)):
			turn_left()
		elif(payload == 'R' and not(is_stopped)):
			turn_right()
		else:
			print('Unknown command')
	elif(str(message.topic) == 'ece180d/team5/speed'):
		payload = message.payload.decode("utf-8")
		print(payload)
		if(payload == '+'):
			speed += 10
			

def turn_left():
	#current time
	start_time = time.time()
	#run for 1 seconds
	while(time.time() - start_time < left_turn_length):
		#drive left motor backward
		io.output(in1, False)
		io.output(in2, True)
		#drive right motor forward
		io.output(in3, True)
		io.output(in4, False)
	#once while loop is over, return to driving straight
	io.output(in1, True)
	io.output(in2, False)
	io.output(in3, True)
	io.output(in4, False)

def turn_right():
	#current time
	start_time = time.time()
	#run for 1 second
	while(time.time() - start_time < right_turn_length):
		#drive left forward
		io.output(in1, True)
		io.output(in2, False)
		#drive right backward
		io.output(in3, False)
		io.output(in4, True)
	#once while loop is over, return to driving straight
	io.output(in1, True)
	io.output(in2, False)
	io.output(in3, True)
	io.output(in4, False)

def stop_driving():
	#drive all inputs high to stop driving
	io.output(in1, True)
	io.output(in2, True)
	io.output(in3, True)
	io.output(in4, True)
	pwmL.stop()
	pwmR.stop()

client = mqtt.Client()

client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message

client.connect_async('mqtt.eclipseprojects.io')

client.loop_start()

##Start Motor control section
io.setmode(io.BCM)

#set up motor pins. 12,13,18,19 are PWM.
in1 = 17
in2 = 27
in3 = 23
in4 = 24
enR = 13
enL = 19

io.setup(in1, io.OUT)
io.setup(in2, io.OUT)
io.setup(in3, io.OUT)
io.setup(in4, io.OUT)
io.setup(enL, io.OUT)
io.setup(enR, io.OUT)

#set up pwm's at 100 Hz
pwmL = io.PWM(enL, 100)
pwmR = io.PWM(enR, 100)

try:
	#start driving straight. Once output is started, it continues outputting High/Low forever until stopped
	pwmL.start(10)
	pwmR.start(10)
	io.output(in1, True)
	io.output(in2, False)
	io.output(in3, True)
	io.output(in4, False)
	time.sleep(20)
	for speed in range(10, 100, 5):
		pwmR.ChangeDutyCycle(speed)
		pwmL.ChangeDutyCycle(speed)
	stop_driving()
except KeyboardInterrupt:
	stop_driving()
	io.cleanup()
	client.loop_stop()
	client.disconnect()

io.cleanup()
client.loop_stop()
client.disconnect()
