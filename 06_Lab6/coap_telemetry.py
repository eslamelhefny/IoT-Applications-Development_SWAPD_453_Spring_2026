import asyncio
import json
from aiocoap import Context, Message, POST

TB_HOST  = "localhost"
TB_TOKEN = "FyJevsYxPrGgLRe1zSqR"  
TB_PORT  = 5683

async def send_telemetry(temp, hum):
    context = await Context.create_client_context()

    uri = f"coap://{TB_HOST}:{TB_PORT}/api/v1/{TB_TOKEN}/telemetry"

    payload = json.dumps({
        "temperature": temp,
        "humidity": hum
    }).encode()

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