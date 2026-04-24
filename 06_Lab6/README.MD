# Advanced IoT Lab — Step-by-Step Implementation Guide

- **Zewail City of Science and Technology — Faculty of Engineering**
- **Prepared by:** Eng. Eslam El Hefny 
- **Semester:** Spring 2026
- **Prerequisites:** ThingsBoard IoT Lab (Introductory)
- **Topics:** MQTT Advanced (QoS, LWT, Retained Messages) & CoAP Protocol

---

## Table of Contents

- [Step 0: Environment Setup](#step-0-environment-setup)
  - [0.1 Install Docker](#01-install-docker)
  - [0.2 Run ThingsBoard Locally](#02-run-thingsboard-locally)
  - [0.3 Create Devices in ThingsBoard](#03-create-devices-in-thingsboard)
  - [0.4 Install Tools on Your PC](#04-install-tools-on-your-pc)
  - [0.5 Arduino IDE Setup (for ESP32 exercises)](#05-arduino-ide-setup-for-esp32-exercises)
  - [0.6 Wireshark Loopback Configuration (Windows)](#06-wireshark-loopback-configuration-windows)
- [Step 1: Exercise 1 — QoS Level Comparison](#step-1-exercise-1--qos-level-comparison)
- [Step 2: Exercise 2 — Last Will and Testament](#step-2-exercise-2--last-will-and-testament)
- [Step 3: Exercise 3 — Retained Messages](#step-3-exercise-3--retained-messages)
- [Step 4: Exercise 4 — CoAP Telemetry with ThingsBoard]
- [step-4-exercise-4--coap-telemetry-with-thingsboard](#step-4-exercise-4--coap-telemetry-with-thingsboard)
- [#Step-5: Exercise 5 — CoAP vs MQTT Performance Comparison]()

---

## Step 0: Environment Setup

### 0.1 Install Docker

**Windows / macOS:**

1. Download Docker Desktop from https://www.docker.com/products/docker-desktop/
2. Install and launch Docker Desktop.
3. Go to **Settings > Resources** and allocate at least **4 GB RAM**.
4. Make sure Docker Desktop is running before proceeding.

**Linux (Ubuntu):**

```bash
sudo apt update
sudo apt install docker.io docker-compose -y
sudo systemctl enable docker
sudo usermod -aG docker $USER
# Log out and back in for group changes to take effect
```

---

### 0.2 Run ThingsBoard Locally

**Windows (PowerShell) — Single Line:**

```powershell
docker run -it -p 9090:9090 -p 1883:1883 -p 7070:7070 -p 5683-5688:5683-5688/udp -v ~/.mytb-data:/data -v ~/.mytb-logs:/var/log/thingsboard --name mytb --restart always thingsboard/tb-postgres
```

> **PowerShell Note:** Do NOT use `\` for line continuation — PowerShell uses backtick `` ` `` instead. The single-line command above is safest.

**Windows (PowerShell) — Multi-Line Alternative:**

```powershell
docker run -it -p 9090:9090 -p 1883:1883 -p 7070:7070 `
  -p 5683-5688:5683-5688/udp `
  -v ~/.mytb-data:/data `
  -v ~/.mytb-logs:/var/log/thingsboard `
  --name mytb --restart always `
  thingsboard/tb-postgres
```

**Linux / macOS (Bash):**

```bash
mkdir -p ~/.mytb-data && mkdir -p ~/.mytb-logs

docker run -it -p 9090:9090 -p 1883:1883 -p 7070:7070 \
  -p 5683-5688:5683-5688/udp \
  -v ~/.mytb-data:/data \
  -v ~/.mytb-logs:/var/log/thingsboard \
  --name mytb --restart always \
  thingsboard/tb-postgres
```

**After Running:**

- Wait 1–2 minutes for ThingsBoard to initialize.
- Open your browser: **http://localhost:9090**
- Login as **Tenant Admin:**
  - **Username:** `tenant@thingsboard.org`
  - **Password:** `tenant`

**Common Docker Commands:**

| Command | Description |
|---------|-------------|
| `docker start mytb` | Start the container (if stopped) |
| `docker stop mytb` | Stop the container |
| `docker logs -f mytb` | Watch live logs (Ctrl+C to stop watching) |
| `docker ps` | Check running containers |
| `docker rm mytb` | Remove container (to recreate from scratch) |

> **Container Name Conflict:** If you get an error saying the name `/mytb` is already in use, the container already exists. Just run `docker start mytb` to start it.

---

### 0.3 Create Devices in ThingsBoard

You need **4 devices** for this lab. For each device:

1. Navigate to **Devices** from the left sidebar.
2. Click the **"+"** button → **Add new device**.
3. Enter the device name and click **Add**.
4. Click on the newly created device → **Credentials** tab.
5. Copy the **Access Token** and save it somewhere.

Create these devices:

| Device Name | Purpose | Token (save yours here) |
|-------------|---------|------------------------|
| `MQTT_QoS_Test` | Exercise 1 — QoS comparison | __________________ |
| `MQTT_LWT_Test` | Exercise 2 & 3 — LWT and Retained | __________________ |
| `CoAP_Sensor_01` | Exercise 4 — CoAP telemetry | __________________ |
| `CoAP_Perf_Test` | Exercise 5 — Performance comparison | __________________ |

---

### 0.4 Install Tools on Your PC

**Python Libraries:**

```bash
pip install paho-mqtt aiocoap
```

**Mosquitto Client Tools (not the broker — just CLI tools):**

- **Windows:** Download from https://mosquitto.org/download/ and install. You do NOT need to run it as a service — just install the files. Add the install path (usually `C:\Program Files\mosquitto\`) to your system PATH.
- **Ubuntu:** `sudo apt install mosquitto-clients -y`
- **macOS:** `brew install mosquitto`

> ** Note:** ThingsBoard has a **built-in MQTT broker** on port 1883. You do NOT need to run a separate Mosquitto broker. You only need the Mosquitto **client tools** (`mosquitto_pub` and `mosquitto_sub`) for Exercise 3.

**CoAP CLI:**

```bash
npm install -g coap-cli
```

**Wireshark:**

Download and install from https://www.wireshark.org/download.html

---

### 1.5 Deliverables

- 3 Wireshark captures (.pcapng files)
- Completed comparison table
- A brief analysis paragraph (100–150 words): Which QoS level is most appropriate for a hospital patient monitoring system, and why?

---

## Step 2: Exercise 2 — Last Will and Testament

**Objective:** Implement and test the LWT mechanism for device failure detection.

### 2.1 Create the LWT Test Script

Save the following as `lwt_test.py`:

```python
import paho.mqtt.client as mqtt
import json
import time

TB_HOST  = "localhost"
TB_PORT  = 1883
TB_TOKEN = "YOUR_MQTT_LWT_Test_TOKEN"  # <-- Replace with your token!

# ===== Callbacks (paho-mqtt v2 API) =====
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

# ===== Setup (paho-mqtt v2 API) =====
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
```

### 2.2 Test Graceful Disconnect

1. Open ThingsBoard → **Devices → MQTT_LWT_Test → Attributes tab** (keep this open).
2. Run the script:
   ```powershell
   python lwt_test.py
   ```
3. Wait for a few telemetry messages to appear.
4. Press **Ctrl+C** to stop gracefully.
5. **Check ThingsBoard:** The `status` attribute should show `"offline"` (published by the client itself).
6. **Take a screenshot** of the Attributes tab.

### 2.3 Test Ungraceful Disconnect (LWT Trigger)

1. Run the script again:
   ```powershell
   python lwt_test.py
   ```
2. **Check ThingsBoard:** Status should show `"online"`. **Take a screenshot.**
3. Now **kill the process forcefully** — open a second PowerShell window and run:
   ```powershell
   taskkill /F /IM python.exe
   ```
   Or simply **close the terminal window** entirely.
4. **Wait 30–90 seconds** for the MQTT keep-alive timeout to expire.
5. **Check ThingsBoard again:** The broker will have published the LWT message and status changes to `"offline"`. **Take a screenshot.**
6. Run the script once more to verify status returns to `"online"`.

### 2.4 Deliverables

- Screenshots of the ThingsBoard Attributes tab showing:
  1. Status = "online" (after connection)
  2. Status = "offline" (after ungraceful disconnect / LWT triggered)
  3. Status = "online" again (after reconnection)

---

## Step 3: Exercise 3 — Retained Messages

**Objective:** Understand how retained messages work and verify their behavior.

### 3.1 Publish a Retained Message

**Terminal 1 — Subscribe first:**

```powershell
mosquitto_sub -h localhost -p 1883 -t "test/retained" -v
```

**Terminal 2 — Publish a retained message:**

```powershell
mosquitto_pub -h localhost -p 1883 -t "test/retained" -m "{\"config\": \"threshold=30\"}" -r
```

> The `-r` flag sets the **retain flag** to true.

**Terminal 1** should show the message immediately.

### 3.2 Test Retention — New Subscriber Gets Old Message

1. **Stop** the subscriber in Terminal 1 (Ctrl+C).
2. **Restart** the subscriber:
   ```powershell
   mosquitto_sub -h localhost -p 1883 -t "test/retained" -v
   ```
3. **Result:** You should **immediately** receive the retained message — even though it was published before you subscribed. This proves the broker stored it.

### 3.3 Replace a Retained Message

In Terminal 2, publish a new retained message to the same topic:

```powershell
mosquitto_pub -h localhost -p 1883 -t "test/retained" -m "{\"config\": \"threshold=45\"}" -r
```

Restart the subscriber again — you'll get the **new** retained message, not the old one.

### 3.4 Delete a Retained Message

Publish an **empty payload** with the retain flag:

```powershell
mosquitto_pub -h localhost -p 1883 -t "test/retained" -m "" -r
```

Restart the subscriber — this time you should get **nothing** because the retained message was deleted.

### 3.5 Wireshark Verification

1. Start Wireshark on Loopback, filter: `mqtt`
2. Repeat steps 3.1–3.4.
3. Click on the PUBLISH packets in Wireshark and expand the **MQTT** section.
4. Look for **"Retain: Set"** in the packet details for retained messages.
5. **Take screenshots** highlighting the Retain flag.

### 3.6 Deliverables

- Wireshark captures showing retain flag set/unset
- Terminal screenshots showing:
  - Subscriber receiving retained message on reconnect
  - Retained message replaced with new value
  - Retained message deleted (empty payload)

---

## Step 4: Exercise 4 — CoAP Telemetry with ThingsBoard

**Objective:** Send sensor data to ThingsBoard using the CoAP protocol.

### 4.1 Verify CoAP Port is Open

```powershell
docker port mytb
```

You should see a line containing: `5683/udp -> 0.0.0.0:5683`

### 4.2 Send Telemetry Using coap-cli

Replace `YOUR_TOKEN` with your **CoAP_Sensor_01** device access token.

```powershell
# Message 1
echo '{"temperature": 24.1, "humidity": 60}' | coap post coap://localhost/api/v1/YOUR_TOKEN/telemetry
```

Expected output: `(2.01)` — means "Created", ThingsBoard accepted the data.

```powershell
# Message 2
echo '{"temperature": 25.3, "humidity": 58}' | coap post coap://localhost/api/v1/YOUR_TOKEN/telemetry
```

```powershell
# Message 3
echo '{"temperature": 27.0, "humidity": 55}' | coap post coap://localhost/api/v1/YOUR_TOKEN/telemetry
```

```powershell
# Message 4
echo '{"temperature": 23.8, "humidity": 62}' | coap post coap://localhost/api/v1/YOUR_TOKEN/telemetry
```

```powershell
# Message 5
echo '{"temperature": 29.5, "humidity": 50}' | coap post coap://localhost/api/v1/YOUR_TOKEN/telemetry
```

### 4.3 Verify in ThingsBoard

Go to **Devices → CoAP_Sensor_01 → Latest Telemetry** tab. You should see the latest `temperature` and `humidity` values.

### 4.4 Send via Python (aiocoap)

Save as `coap_telemetry.py`:

```python
import asyncio
import json
from aiocoap import Context, Message, POST

TB_HOST  = "localhost"
TB_TOKEN = "YOUR_CoAP_Sensor_01_TOKEN"  # <-- Replace!
TB_PORT  = 5683

async def send_telemetry(temp, hum):
    context = await Context.create_client_context()
    uri = f"coap://{TB_HOST}:{TB_PORT}/api/v1/{TB_TOKEN}/telemetry"
    payload = json.dumps({"temperature": temp, "humidity": hum}).encode()
    request = Message(code=POST, uri=uri, payload=payload)

    try:
        response = await context.request(request).response
        print(f"Sent temp={temp}, hum={hum} -> Response: {response.code}")
    except Exception as e:
        print(f"Failed: {e}")

async def main():
    readings = [(24.5, 61), (26.0, 58), (28.3, 54), (22.1, 67), (30.0, 49)]
    for temp, hum in readings:
        await send_telemetry(temp, hum)
        await asyncio.sleep(1)

asyncio.run(main())
```

Run it:

```powershell
python coap_telemetry.py
```

You should see `Response: 2.01` for each reading.

### 4.5 Capture in Wireshark

1. Start Wireshark on Loopback, filter: `coap` or `udp.port == 5683`
2. Re-send one of the coap-cli commands.
3. **Observe:**
   - **CON POST** — Confirmable POST request from your PC
   - **ACK 2.01 Created** — Acknowledgment from ThingsBoard
4. Click on the CON packet and expand the CoAP section. Note:
   - Message Type: CON (Confirmable)
   - Method Code: POST
   - URI-Path options: `api`, `v1`, `{token}`, `telemetry`
5. **Take screenshots** of the Wireshark capture and ThingsBoard telemetry tab.

### 4.6 Deliverables

- coap-cli terminal output showing `(2.01)` responses
- Python script output
- Wireshark CoAP capture screenshot
- ThingsBoard Latest Telemetry tab screenshot

---

## Step 5: Exercise 5 — CoAP vs MQTT Performance Comparison

**Objective:** Quantitatively compare MQTT and CoAP protocol overhead.

### 5.1 Create the MQTT Performance Script

Save as `mqtt_perf.py`:

```python
import paho.mqtt.client as mqtt
import json
import time

TB_HOST  = "localhost"
TB_PORT  = 1883
TB_TOKEN = "YOUR_MQTT_QoS_Test_TOKEN"  # <-- Replace!
NUM = 50

connected = False

def on_connect(client, userdata, flags, rc, properties):
    global connected
    connected = True
    print(f"MQTT connected (rc={rc})")

# paho-mqtt v2 API
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "MQTT_Perf")
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
```

### 5.2 Create the CoAP Performance Script

Save as `coap_perf.py`:

```python
import asyncio
import json
import time
from aiocoap import Context, Message, POST

TB_HOST  = "localhost"
TB_TOKEN = "YOUR_CoAP_Perf_Test_TOKEN"  # <-- Replace!
TB_PORT  = 5683
NUM = 50

async def main():
    context = await Context.create_client_context()
    uri = f"coap://{TB_HOST}:{TB_PORT}/api/v1/{TB_TOKEN}/telemetry"

    print(f"Sending {NUM} messages via CoAP CON...")
    start = time.time()

    for i in range(1, NUM + 1):
        payload = json.dumps({"temperature": 20 + (i * 0.2), "humidity": 50, "seq": i}).encode()
        request = Message(code=POST, uri=uri, payload=payload)
        try:
            response = await context.request(request).response
        except Exception as e:
            print(f"  msg {i} failed: {e}")
        await asyncio.sleep(0.1)

    elapsed = time.time() - start
    print(f"\nDone! {NUM} messages in {elapsed:.2f}s ({elapsed/NUM*1000:.1f}ms avg)")

asyncio.run(main())
```

### 5.3 Run Both with Wireshark

**Session 1: MQTT**

1. Start Wireshark capture on Loopback, filter: `tcp.port == 1883`
2. Run:
   ```powershell
   python mqtt_perf.py
   ```
3. Stop capture → Save as `mqtt_perf.pcapng`
4. Go to **Statistics > Protocol Hierarchy** and note total bytes & packets.

**Session 2: CoAP**

1. Start new Wireshark capture on Loopback, filter: `udp.port == 5683`
2. Run:
   ```powershell
   python coap_perf.py
   ```
3. Stop capture → Save as `coap_perf.pcapng`
4. Note the same stats.

### 5.4 Fill the Comparison Table

| Metric | MQTT (QoS 1) | CoAP (CON) |
|--------|-------------|------------|
| Total packets | ___ | ___ |
| Total bytes transferred | ___ | ___ |
| Avg latency per message | ___ ms | ___ ms |
| Connection setup packets | 3 (TCP handshake) + 2 (CONNECT/CONNACK) = 5 | 0 (connectionless) |
| Packets per message | 2 (PUBLISH + PUBACK) | 2 (CON + ACK) |

### 5.5 Expected Findings

- CoAP typically has **less total overhead** because there's no TCP handshake, no persistent connection, and no MQTT CONNECT/CONNACK.
- MQTT wins for **sustained streaming** because the TCP connection is reused for all 50 messages.
- CoAP has a smaller header (4 bytes fixed vs MQTT's 2+ bytes variable).
- TCP adds per-packet overhead (20-byte TCP header vs 8-byte UDP header).

### 5.6 Deliverables

- 2 Wireshark captures (.pcapng files)
- Completed comparison table
- A bar chart visualizing the results (total bytes and total packets side by side)
- 200-word analysis: Which protocol is more efficient for this scenario, and in what conditions would the result change?

---

## Step 6: Exercise 6 (Bonus) — ESP32 Dual Protocol

**Objective:** Build an ESP32 system that switches between MQTT and CoAP at runtime.

### 6.1 Wire the Hardware

| Component | ESP32 Pin | Notes |
|-----------|-----------|-------|
| DHT22 VCC | 3.3V | Power supply |
| DHT22 GND | GND | Ground |
| DHT22 DATA | GPIO 4 | 10KΩ pull-up to 3.3V |
| Built-in LED | GPIO 2 | Status indicator |
| BOOT Button | GPIO 0 | Protocol toggle (built-in on most boards) |

### 6.2 Upload the Sketch

```cpp
#include <WiFi.h>
#include <PubSubClient.h>
#include <WiFiUdp.h>
#include <coap-simple.h>
#include <DHT.h>
#include <ArduinoJson.h>

// ===== Configuration =====
#define WIFI_SSID     "YOUR_SSID"
#define WIFI_PASSWORD "YOUR_PASS"
#define TB_HOST       "YOUR_PC_IP"  // e.g., "192.168.1.100"
#define MQTT_TOKEN    "YOUR_MQTT_LWT_Test_TOKEN"
#define COAP_TOKEN    "YOUR_CoAP_Sensor_01_TOKEN"
#define BUTTON_PIN    0
#define DHT_PIN       4
#define DHT_TYPE      DHT22
#define LED_PIN       2
#define SEND_INTERVAL 5000

// ===== Objects =====
WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);
WiFiUDP udp;
Coap coap(udp);
DHT dht(DHT_PIN, DHT_TYPE);

bool useMQTT = true;
unsigned long lastSend = 0;
bool lastButtonState = HIGH;

// ===== CoAP Response Callback =====
void coapResponse(CoapPacket &pkt, IPAddress ip, int port) {
    Serial.print("[CoAP] Response code: ");
    Serial.println(pkt.code);
}

// ===== WiFi Connection =====
void connectWiFi() {
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    Serial.print("WiFi connecting");
    while (WiFi.status() != WL_CONNECTED) {
        delay(500); Serial.print(".");
    }
    Serial.println("\nWiFi connected: " + WiFi.localIP().toString());
}

// ===== MQTT Connection with LWT =====
void connectMQTT() {
    if (mqttClient.connected()) return;
    mqttClient.setServer(TB_HOST, 1883);
    while (!mqttClient.connected()) {
        Serial.print("[MQTT] Connecting...");
        if (mqttClient.connect("ESP32_Dual", MQTT_TOKEN, NULL,
            "v1/devices/me/attributes", 1, true,
            "{\"status\":\"offline\"}")) {
            mqttClient.publish("v1/devices/me/attributes",
                "{\"status\":\"online\"}", true);
            Serial.println("connected!");
        } else {
            Serial.print("failed, rc=");
            Serial.println(mqttClient.state());
            delay(3000);
        }
    }
}

// ===== Setup =====
void setup() {
    Serial.begin(115200);
    pinMode(BUTTON_PIN, INPUT_PULLUP);
    pinMode(LED_PIN, OUTPUT);
    dht.begin();
    connectWiFi();
    connectMQTT();
    coap.response(coapResponse);
    coap.start();
    Serial.println("\n=== Starting in MQTT mode ===");
    Serial.println("Press BOOT button to toggle between MQTT and CoAP\n");
}

// ===== Loop =====
void loop() {
    mqttClient.loop();
    coap.loop();

    // Check button press (toggle protocol)
    bool btn = digitalRead(BUTTON_PIN);
    if (btn == LOW && lastButtonState == HIGH) {
        useMQTT = !useMQTT;
        digitalWrite(LED_PIN, useMQTT ? LOW : HIGH);  // LED ON = CoAP mode
        Serial.println(useMQTT ?
            "\n>>> Switched to MQTT <<<\n" :
            "\n>>> Switched to CoAP <<<\n");
        if (useMQTT) connectMQTT();
        delay(300);  // debounce
    }
    lastButtonState = btn;

    // Send telemetry at regular intervals
    if (millis() - lastSend > SEND_INTERVAL) {
        lastSend = millis();
        float temp = dht.readTemperature();
        float hum  = dht.readHumidity();
        if (isnan(temp) || isnan(hum)) {
            Serial.println("DHT read failed!");
            return;
        }

        char payload[128];
        snprintf(payload, sizeof(payload),
            "{\"temperature\":%.1f,\"humidity\":%.1f,\"protocol\":\"%s\"}",
            temp, hum, useMQTT ? "MQTT" : "CoAP");

        if (useMQTT) {
            if (!mqttClient.connected()) connectMQTT();
            mqttClient.publish("v1/devices/me/telemetry", payload);
            Serial.print("[MQTT] ");
        } else {
            IPAddress tbIP;
            WiFi.hostByName(TB_HOST, tbIP);
            String path = String("api/v1/") + COAP_TOKEN + "/telemetry";
            coap.post(tbIP, 5683, path.c_str(), payload);
            Serial.print("[CoAP] ");
        }
        Serial.println(payload);
    }
}
```

### 6.3 Test the Dual Protocol System

1. Upload the sketch to ESP32.
2. Open Serial Monitor at **115200 baud**.
3. You'll see `[MQTT] {...}` messages being sent every 5 seconds.
4. Press the **BOOT button** → toggles to `[CoAP] {...}`. LED turns ON.
5. Press again → back to `[MQTT]`. LED turns OFF.
6. Open Wireshark (on your main network adapter, NOT loopback — since ESP32 is a separate device on the network).
7. Capture with no filter and observe the transition from **TCP (port 1883)** to **UDP (port 5683)** traffic.

### 6.4 ThingsBoard Dashboard

1. Create a new dashboard: **"Dual Protocol Monitor"**
2. Add a **Time Series Line Chart** showing telemetry from both MQTT_LWT_Test and CoAP_Sensor_01.
3. Add a **Value Card** showing the `protocol` attribute.
4. Take screenshots of the dashboard with data from both protocols.

### 6.5 Deliverables

- Complete Arduino code (uploaded sketch)
- Serial Monitor screenshots showing protocol switching
- Wireshark capture showing transition from TCP/MQTT to UDP/CoAP
- ThingsBoard dashboard screenshot

---

## Summary Checklist

| Exercise | Key Deliverables | Status |
|----------|-----------------|--------|
| **Ex 1 — QoS** | 3 Wireshark captures, comparison table, analysis paragraph | ☐ |
| **Ex 2 — LWT** | Screenshots of online/offline status transitions | ☐ |
| **Ex 3 — Retained** | Wireshark captures showing retain flag, terminal results | ☐ |
| **Ex 4 — CoAP** | coap-cli output, Python output, Wireshark capture, telemetry screenshot | ☐ |
| **Ex 5 — Performance** | 2 Wireshark captures, comparison table, bar chart, 200-word analysis | ☐ |
| **Ex 6 — Dual (Bonus)** | Arduino code, Serial Monitor output, Wireshark capture, dashboard | ☐ |

---

## Troubleshooting

### Docker Issues

| Problem | Solution |
|---------|----------|
| Container name "/mytb" already in use | Run `docker start mytb` instead of `docker run` |
| ThingsBoard not loading on localhost:9090 | Wait 2 minutes, then check `docker logs -f mytb` for errors |
| Port 1883 already in use | Stop any local Mosquitto broker: `net stop mosquitto` (Windows) |
| Container keeps restarting | Check logs: `docker logs mytb` — may need more RAM |

### Python / paho-mqtt Issues

| Problem | Solution |
|---------|----------|
| `ValueError: Unsupported callback API version` | You have paho-mqtt v2. Use `mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "client_id")` and add `properties` parameter to all callbacks |
| `ConnectionRefusedError` | Check Docker is running: `docker ps`. Check port 1883 is mapped. |

### PowerShell Issues

| Problem | Solution |
|---------|----------|
| `Missing expression after unary operator '--'` | PowerShell doesn't support `\` for line continuation. Use backtick `` ` `` or paste as single line. |

### Wireshark Issues

| Problem | Solution |
|---------|----------|
| No MQTT/CoAP packets captured | You're capturing on the wrong interface. Use **Loopback adapter** for localhost traffic. |
| No loopback adapter visible | Reinstall Npcap from npcap.com with **"Support loopback traffic"** checked. |
| CoAP packets show as "UDP" not "CoAP" | Right-click packet → **Decode As** → set UDP port 5683 to CoAP. |

### CoAP Issues

| Problem | Solution |
|---------|----------|
| `coap: command not found` | Install: `npm install -g coap-cli` |
| Connection timeout on CoAP | Verify port 5683/udp is mapped: `docker port mytb` |
| aiocoap import error | Install: `pip install aiocoap` |

### ESP32 Issues

| Problem | Solution |
|---------|----------|
| ESP32 can't connect to ThingsBoard | Use your PC's local IP (e.g., 192.168.1.x), NOT "localhost" |
| DHT read failed | Check wiring: DATA → GPIO 4 with 10KΩ pull-up to 3.3V |
| CoAP library not found | Install "CoAP simple library" by Hirotaka Niisato from Library Manager |

---

**Good luck! — Eng. Eslam El Hefny**
