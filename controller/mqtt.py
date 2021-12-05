import paho.mqtt.client as mqtt

class Mqtt(object):
    '''Class wrapping all game controller MQTT communication.'''
    def __init__(self):
        '''Set up MQTT client and connect to broker.'''
        self.speedTopic = "ece180d/team5/speed"
        self.gameTopic = "ece180d/team5/game"

        self.client = mqtt.Client()
        self.client.on_connect = onConnect
        self.client.on_disconnect = onDisconnect
        self.client.connect_async("mqtt.eclipseprojects.io")
        self.client.loop_start()

    def stop(self):
        '''Clean up MQTT client before exiting.'''
        self.client.loop_stop()
        self.client.disconnect()

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

# Callback functions

def onConnect(client, userdata, flags, rc):
    if rc != 0:
        print("Failed to connect to MQTT broker")
    else:
        print("Connected")

def onDisconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnect")
    else:
        print("Disconnected")