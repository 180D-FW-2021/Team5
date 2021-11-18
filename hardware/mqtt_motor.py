import paho.mqtt.client as mqtt
import RPi.GPIO as io
import time

left_forward = True
right_forward = True

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
		print(str(message.payload))
		if(str(message.payload) == 'L'):
			turn_left()
		elif(str(message.payload) == 'R'):
			turn_right()
		else:
			print('Unknown command')

def turn_left():
	#current time
	start_time = time.time()
	#run for 1 seconds
	while(time.time() - start_time < 2):
		io.output(in1, True)
		io.output(in2, False)
	#once while loop is over, return to driving straight
	io.output(in1, False)
	io.output(in2, True)
	#io.output(in3, False)
	#io.output(in4, True)

def turn_right():
	#current time
	start_time = time.time()
	#run for 1 second
	while(time.time() - start_time < 2):
		io.output(in1, False)
		io.output(in2, True)
	#once while loop is over, return to driving straight
	io.output(in1, False)
	io.output(in2, True)
	#io.output(in3, False)
	#io.output(in4, True)

def stop_driving():
	io.output(in1, True)
	io.output(in2, True)
	#io.output(in3, True)
	#io.output(in4, True)

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
#in3 = 18
#in4 = 12
#enL = 5
enR = 18

io.setup(in1, io.OUT)
io.setup(in2, io.OUT)
#io.setup(in3, io.OUT)
#io.setup(in4, io.OUT)
#io.setup(enL, io.OUT)
io.setup(enR, io.OUT)

#set up pwm's at 100 Hz
#pwmL = io.PWM(enL, 100)
#pwmR = io.PWM(enR, 50)

try:
	#start driving straight. Once output is started, it continues outputting High/Low forever until stopped
	#pwmL.start(10)
	#pwmR.start(100)
	io.output(in1, False)
	io.output(in2, True)
	io.output(enR, True)
	#io.output(in3, False)
	#io.output(in4, True)
	time.sleep(20)
	#pwmR.ChangeDutyCycle(100)
	stop_driving()
except KeyboardInterrupt:
	stop_driving()
	#pwmR.stop()
	io.cleanup()
	client.loop_stop()
	client.disconnect()

#pwmL.stop()
#pwmR.stop()
io.cleanup()
client.loop_stop()
client.disconnect()
