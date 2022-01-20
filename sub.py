import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("my/msg")

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload.decode('utf-8')))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
#client.username_pw_set(username="kebbimqtt",password="IoeoK2hK5Wti")
client.username_pw_set(username="webduinomqtt",password="ItiK5oeoK2hW")
client.connect("mqtt1.webduino.io", 1883, 60)
client.loop_forever()

