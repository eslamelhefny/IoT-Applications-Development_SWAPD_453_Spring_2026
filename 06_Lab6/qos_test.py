import paho.mqtt.client as mqtt
import time
import json
import sys

# ===== Configuration =====
TB_HOST  = "localhost"
TB_PORT  = 1883
TB_TOKEN = "LrX8RgTGFtkKJfj6l2Tn"  
TOPIC    = "v1/devices/me/telemetry"

qos_level = int(sys.argv[1]) if len(sys.argv) > 1 else 0
NUM_MESSAGES = 10

# ===== Callbacks (v2 API) =====
def on_connect(client, userdata, flags, rc, properties):
    if rc == 0:
        print(f"Connected to ThingsBoard (QoS test level {qos_level})")
    else:
        print(f"Connection failed, rc={rc}")

def on_publish(client, userdata, mid, rc, properties):
    print(f"  Published msg id={mid}")

# ===== Setup (v2 API) =====
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "QoS_Tester")
client.username_pw_set(TB_TOKEN)
client.on_connect = on_connect
client.on_publish = on_publish

client.connect(TB_HOST, TB_PORT)
client.loop_start()
time.sleep(2)

# ===== Publish Messages =====
print(f"\n--- Sending {NUM_MESSAGES} messages with QoS {qos_level} ---\n")

for i in range(1, NUM_MESSAGES + 1):
    payload = json.dumps({
        "temperature": 20 + i,
        "humidity": 50 + i,
        "msg_number": i,
        "qos_level": qos_level
    })
    result = client.publish(TOPIC, payload, qos=qos_level)
    print(f"  [{i}/{NUM_MESSAGES}] Sent: {payload}")
    time.sleep(0.5)

time.sleep(3)
client.loop_stop()
client.disconnect()
print(f"\n--- Done (QoS {qos_level}) ---")



# mosquitto_pub -h localhost -p 1883 -t "v1/devices/me/telemetry" -u "LrX8RgTGFtkKJfj6l2Tn" -m "{\"test\": 123}"