import paho.mqtt.client as mqtt
import json
import time

TB_HOST  = "localhost"
TB_PORT  = 1883
TB_TOKEN = "YOUR_MQTT_QoS_Test_TOKEN"  # Reuse from Exercise 1
NUM = 50

connected = False

def on_connect(client, ud, flags, rc):
    global connected
    connected = True
    print(f"MQTT connected (rc={rc})")

client = mqtt.Client("MQTT_Perf")
client.username_pw_set(TB_TOKEN)
client.on_connect = on_connect
client.connect(TB_HOST, TB_PORT)
client.loop_start()

while not connected:
    time.sleep(0.1)

print(f"Sending {NUM} messages via MQTT QoS 1...")
start = time.time()

for i in range(1, NUM + 1):
    payload = json.dumps({"temperature": 20 + (i * 0.2), "humidity": 50, "seq": i})
    client.publish("v1/devices/me/telemetry", payload, qos=1)
    time.sleep(0.1)

elapsed = time.time() - start
time.sleep(2)
client.disconnect()
print(f"\nDone! {NUM} messages in {elapsed:.2f}s ({elapsed/NUM*1000:.1f}ms avg)")