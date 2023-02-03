import asyncio
import config
import datetime
import json
import logging
import websockets

async def main():
    async with websockets.connect(config.WEBSOCKET_URL) as websocket:
        logging.info(f'Connected to {config.WEBSOCKET_URL}.')

        while True:
            message = await websocket.recv()

            data = json.loads(message)

            if data['event'] == config.PLAYSOUND_EVENT_TYPE:
                logging.info(f"Received playsound event: {data}")

                with open(config.TIMESTAMP_FILE, 'w+') as f:
                    f.write(datetime.datetime.now(datetime.timezone.utc).isoformat())

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format=config.LOGGING_FORMAT)

    asyncio.run(main())