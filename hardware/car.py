import RPi.GPIO as io
import time 

class Car:
	def __init__(self, in1, in2, in3, in4, enL, enR):
        #Start Motor control section
        io.setmode(io.BCM)
        
        self.in1 = in1
        self.in2 = in2
        self.in3 = in3
        self.in4 = in4
        self.enL = enL
        self.enR = enR

        io.setup(self.in1, io.OUT)
        io.setup(self.in2, io.OUT)
        io.setup(self.in3, io.OUT)
        io.setup(self.in4, io.OUT)
        io.setup(self.enL, io.OUT)
        io.setup(self.enR, io.OUT)

        #set up pwm's at 100 Hz
        self.pwmL = io.PWM(self.enL, 100)
        self.pwmR = io.PWM(self.enR, 100)

        self.is_stopped = False
        self.game_over = False
        self.speed = 20

        self.left_turn_length = 0.4
        self.right_turn_length = 0.5

        self.start_Driving()

	def stop_Driving(self):
		#drive all inputs high to stop driving
		io.output(self.in1, True)
		io.output(self.in2, True)
		io.output(self.in3, True)
		io.output(self.in4, True)
		self.pwmL.stop()
		self.pwmR.stop()

	def start_Driving(self):
		self.pwmL.start(self.speed)
		self.pwmR.start(self.speed)
		io.output(self.in1, True)
		io.output(self.in2, False)
		io.output(self.in3, True)
		io.output(self.in4, False)

	def change_Speed(self, inputSpeed):
		self.speed = inputSpeed
		self.pwmR.ChangeDutyCycle(self.speed)
		self.pwmL.ChangeDutyCycle(self.speed)

	def turn_left(self):
		if(self.is_stopped == True):
			pass
		else:
			#current time
			start_time = time.time()
			#run for 1 seconds
			while(time.time() - start_time < left_turn_length):
				#drive left motor backward
				io.output(self.in1, False)
				io.output(self.in2, True)
				#drive right motor forward
				io.output(self.in3, True)
				io.output(self.in4, False)
			#once while loop is over, return to driving straight
			io.output(self.in1, True)
			io.output(self.in2, False)
			io.output(self.in3, True)
			io.output(self.in4, False)

	def turn_right(self):
        if(self.is_stopped == True):
            pass
        else:
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