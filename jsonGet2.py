import ssl
import paho.mqtt.client as mqtt
from config import broker_address, port, user, password, topic2


def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed", client, userdata, mid, granted_qos)


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
        global Connected
        Connected = True
    else:
        print("Connection failed")


def on_message(client, userdata, message):
    print(f"Message received: {message.payload}")
    jsonString = message.payload
    dict_str = jsonString.decode("UTF-8")
    global jsonData
    jsonData = dict_str
    file1 = open("var2.txt", "w+")
    file1.write(str(jsonData))


Connected = False

client = mqtt.Client("kazanka2")
client.username_pw_set(user, password=password)
client.on_connect = on_connect
client.on_message = on_message
client.on_subscribe = on_subscribe
client.tls_set(r"rootCA.crt", tls_version=ssl.PROTOCOL_TLSv1_2)
client.tls_insecure_set(True)
client.connect(broker_address, port=port)
client.subscribe(topic2)

client.loop_start()
