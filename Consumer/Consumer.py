from confluent_kafka import Consumer, KafkaException, KafkaError # type: ignore
import json
import asyncio
import websockets

kafka_config = {
    'bootstrap.servers': '192.168.137.45:9092',
    'group.id': 'distanta-consumer-group',
    'auto.offset.reset': 'earliest'
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
        print(f"\nDistanta: {data['distanta']:.2f} cm")
    elif topic == 'temperatura_1':
        dateGramada['Temperatura'] = data.get('temperatura')
        dateGramada['Umiditate'] = data.get('umiditate')
        print(f"\nTemperatura: {data.get('temperatura'):.1f}C")
        print(f"Umiditate: {data.get('umiditate'):.1f}%")

async def start_consumer():
    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    raise KafkaException(msg.error())
            proc_mesaj(msg)
    finally:
        consumer.close()

async def trimite_date(websocket, path):
    while True:
        await websocket.send(json.dumps(dateGramada))
        await asyncio.sleep(1)

async def main():
    start_server = websockets.serve(trimite_date, "0.0.0.0", 2323)
    await start_server

    await start_consumer()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.run_forever()