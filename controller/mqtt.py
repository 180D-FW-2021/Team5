from tabnanny import verbose
import paho.mqtt.client as mqtt

class Mqtt(object):
    '''Base class wrapping a generic MQTT client'''
    def __init__(self, verbose=False):
        '''Set up MQTT client and connect to broker.'''
        self.verbose = verbose
        self.client = mqtt.Client()
        self.client.on_connect = self.onConnect
        self.client.on_disconnect = self.onDisconnect
        self.client.on_message = self.onMessage
        self.client.connect_async("test.mosquitto.org")
        self.client.loop_start()

    def stop(self):
        '''Clean up MQTT client before exiting.'''
        self.client.loop_stop()
        self.client.disconnect()

    def onConnect(self, client, userdata, flags, rc):
        '''Default connection logic'''
        if rc != 0:
            print("Failed to connect to MQTT broker")
        else:
            if self.verbose:
                print("Connected")

    def onDisconnect(self, client, userdata, rc):
        '''Default disconnect logic'''
        if rc != 0:
            print("Unexpected disconnect")
        else:
            if self.verbose:
                print("Disconnected")

    def onMessage(self, client, userdata, message):
        '''Default message-handling logic'''
        raise NotImplementedError('No message handling given')

class ControllerMqtt(Mqtt):
    '''Class wrapping all game controller MQTT communication.'''
    def __init__(self):
        '''Set up MQTT client and connect to broker.'''
        super.__init__(True)
        self.speedTopic = "ece180d/team5/speed"
        self.gameTopic = "ece180d/team5/game"

    def startGame(self):
        self.client.publish(self.gameTopic, "start car", qos=1)

    def pauseGame(self):
        self.client.publish(self.gameTopic, "stop car", qos=1)

    def endGame(self):
        self.client.publish(self.gameTopic, "game over", qos=1)

    def activatePower(self):
        self.client.publish(self.gameTopic, "activate power", qos=1)

    def speedUp(self):
        self.client.publish(self.speedTopic, "+", qos=1)

    def speedDown(self):
        self.client.publish(self.speedTopic, "-", qos=1)

class HeartbeatMqtt(Mqtt):
    def __init__(self):
        super().__init__()
        self.imuTopic = "ece180d/team5/imuReady"
        self.carTopic = "ece180d/team5/carReady"
        self.imu = False
        self.car = False

    def onConnect(self, client, userdata, flags, rc):
        if rc != 0:
            raise RuntimeError("Failed to connect to MQTT broker")
        else:
            if self.verbose:
                print("Connected")
            client.subscribe(self.imuTopic, qos=1)
            client.subscribe(self.carTopic, qos=1)

    def onMessage(self, client, userdata, message):
        payload = message.payload.decode("utf-8")
        if str(message.topic) == self.imuTopic and payload == "R":
            self.imu = True
        elif str(message.topic) == self.carTopic and payload == "R":
            self.car = True

    def sendHeartbeat(self):
        for topic in (self.imuTopic, self.carTopic):
            self.client.publish(topic, "?", qos=1)