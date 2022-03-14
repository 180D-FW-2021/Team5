import paho.mqtt.client as mqtt
from queue import Queue

# 0. define callbacks - functions that run when events happen.
# The callback for when the client receives a CONNACK response from the server.

class Subscriber(object):
    def __init__(self, queue):
        self.q = queue

    def on_connect(self, client, userdata, flags, rc):
        print("Connection returned result: "+str(rc))
        
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe("ece180d/gui", qos=1)

    # The callback of the client when it disconnects.
    def on_disconnect(self, client, userdata, rc):
        if rc != 0:
            print("Unexpected Disconnect")
        else:
            print("Expected Disconnect")

    # The default message callback.
    # (you can create separate callbacks per subscribed topic)
    def on_message(self, client, userdata, message):
        self.q.put(str(message.payload))
        #print(str(message.payload))
        

    # 1. create a client instance.

    def init(self):
        client = mqtt.Client()

    # add additional client options (security, certifications, etc.)
    # many default options should be good to start off.
    # add callbacks to client.
        client.on_connect = self.on_connect
        client.on_disconnect = self.on_disconnect
        client.on_message = self.on_message

    # 2. connect to a broker using one of the connect*() functions.
        client.connect_async("mqtt.eclipseprojects.io")
        return client

    # 3. call one of the loop*() functions to maintain network traffic flow with the broker.
    def run(self,client):
        client.loop_start()
        print("subscribe start")
        """try:
            while True:
            pass
        except KeyboardInterrupt:
            stop()"""
        
    def stop(self,client):
        client.loop_stop()
        client.disconnect()
