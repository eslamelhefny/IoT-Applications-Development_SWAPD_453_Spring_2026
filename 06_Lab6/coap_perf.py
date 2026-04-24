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