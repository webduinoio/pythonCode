import network, ubinascii
from umqtt.simple import MQTTClient
from webduino.debug import debug

class MQTT:
    
    def connect(server = 'mqtt1.webduino.io',user ='webduino' ,pwd='webduino'):
        MQTT.server = server
        MQTT.user = user
        MQTT.pwd = pwd
        mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode().replace(':','')
        MQTT.client = MQTTClient('wa'+mac, server, user=user, password=pwd)
        state = True if MQTT.client.connect() == 0 else False
        try:
            debug.print("resubscribe:",MQTT.subTopic)
            MQTT.sub(MQTT.subTopic,MQTT.callback)
        except:
            pass
        return state
        
    def pub(topic,msg):
        MQTT.client.publish(topic,msg)

    def sub(topic,cb):
        MQTT.subTopic = topic
        MQTT.callback = cb
        MQTT.client.set_callback(cb)
        MQTT.client.subscribe(topic)

    def checkMsg():
        try:
            MQTT.client.check_msg()
        except:
            pass
