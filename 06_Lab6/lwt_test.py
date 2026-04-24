import paho.mqtt.client as mqtt
import json
import time

TB_HOST  = "localhost"
TB_PORT  = 1883
TB_TOKEN = "3GK3Kniu9bAg5MX5yzu3"  

def on_connect(client, userdata, flags, rc, properties):
    if rc == 0:
        print("Connected! Publishing 'online' status...")
        client.publish(
            "v1/devices/me/attributes",
            json.dumps({"status": "online"}),
            qos=1, retain=True
        )
        print("Status: ONLINE")
    else:
        print(f"Connection failed: {rc}")

def on_disconnect(client, userdata, flags, rc, properties):
    print(f"Disconnected! rc={rc}")


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "LWT_Tester")
client.username_pw_set(TB_TOKEN)
client.on_connect = on_connect
client.on_disconnect = on_disconnect

# Set Last Will BEFORE connecting
client.will_set(
    topic="v1/devices/me/attributes",
    payload=json.dumps({"status": "offline"}),
    qos=1,
    retain=True
)

client.connect(TB_HOST, TB_PORT)
client.loop_start()
time.sleep(2)

print("\nSending telemetry every 2 seconds. Press Ctrl+C to stop gracefully,")
print("or CLOSE THE TERMINAL to simulate a crash (ungraceful disconnect).\n")

count = 0
try:
    while True:
        count += 1
        payload = json.dumps({"temperature": 22 + count * 0.5, "humidity": 55})
        client.publish("v1/devices/me/telemetry", payload, qos=1)
        print(f"  Telemetry #{count}: {payload}")
        time.sleep(2)
except KeyboardInterrupt:
    print("\nGraceful shutdown - publishing offline status...")
    client.publish(
        "v1/devices/me/attributes",
        json.dumps({"status": "offline"}),
        qos=1, retain=True
    )
    time.sleep(1)
    client.disconnect()
    print("Disconnected gracefully. LWT will NOT be published by broker.")