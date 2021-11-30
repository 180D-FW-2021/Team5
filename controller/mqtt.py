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
        client.publish(self.gameTopic, "start", qos=1)

    def pauseGame(self):
        client.publish(self.gameTopic, "stop", qos=1)

    def endGame(self):
        client.publish(self.gameTopic, "over", qos=1)

    def speedUp(self):
        client.publish(self.speedTopic, "+", qos=1)

    def speedDown(self):
        client.publish(self.speedTopic, "-", qos=1)

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