from confluent_kafka import Consumer, KafkaException, KafkaError  # type: ignore
import json
import asyncio
import websockets
from datetime import datetime 
from dotenv import load_dotenv
import os

load_dotenv()

IP_raspberry_pi = os.getenv("RASPBERRY_PI_IP")

kafka_config = {
    'bootstrap.servers': f'{IP_raspberry_pi}:9092',
    'group.id': 'distanta-consumer-group',
    'auto.offset.reset': 'latest'
}

consumer = Consumer(kafka_config)
consumer.subscribe(['distanta_1', 'temperatura_1'])

dateGramada = {
    'Distanta': None,
    'Temperatura': None,
    'Umiditate': None
}

def proc_mesaj(msg):

    topic = msg.topic()
    data = json.loads(msg.value().decode('utf-8'))

    if topic == 'distanta_1':
        dateGramada['Distanta'] = data['distanta']

    elif topic == 'temperatura_1':
        dateGramada['Temperatura'] = data.get('temperatura')
        dateGramada['Umiditate'] = data.get('umiditate')


async def start_consumer():

    try:
        while True:
            msg = consumer.poll(timeout=0.1)
            if msg is None:
                await asyncio.sleep(0.1)  
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    raise KafkaException(msg.error())
            proc_mesaj(msg)
            await asyncio.sleep(0.1)
    finally:
        consumer.close()

async def trimite_date(websocket, path=""):

    while True:
        await websocket.send(json.dumps(dateGramada))
        await asyncio.sleep(.3)

async def main():

    start_server = websockets.serve(trimite_date, "0.0.0.0", 2323)
    consumer_task = asyncio.create_task(start_consumer())

    await start_server
    await consumer_task


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.run_forever()