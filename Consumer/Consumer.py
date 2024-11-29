#venv\Scripts\activate

from confluent_kafka import Consumer, KafkaException, KafkaError # type: ignore
import json
import threading
import asyncio
import websockets

kafka_config = {
    'bootstrap.servers': '192.168.137.45:9092',  
    'group.id': 'distanta-consumer-group',
    'auto.offset.reset': 'earliest'
}

consumer = Consumer(kafka_config)

topic = ['distanta_1', 'temperatura_1']

consumer.subscribe(topic)

dateGramada = {
    'Distanta': None,
    'Temperatura': None,    
    'Umiditate': None
}

def proc_mesaj(msg):

    topic = msg.topic()

    data = json.loads(msg.value().decode('utf-8'))

    if topic == 'distanta_1':

        distanta = data['distanta']

        dateGramada['Distanta'] = distanta

        print(f"\nDistanta: {distanta:.2f} cm")

    elif topic == 'temperatura_1':

        temp = data.get('temperatura')
        umid = data.get('umiditate')
        
        dateGramada['Temperatura'] = temp
        dateGramada['Umiditate'] = umid

        print(f"\nTemperatura: {temp:.1f}C")
        print(f"Umiiditate: {umid:.1f}%")

def start_consumer():
    try:
        while True:
            msg = consumer.poll(timeout=1.0)

            if msg is None:
                continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF: # type: ignore
                    continue

                else:
                    raise KafkaException(msg.error())
                
            proc_mesaj(msg)

    finally:
        consumer.close()

consumer_thread = threading.Thread(target=start_consumer)
consumer_thread.start()

async def trimite_date(websocket):
    while True:
        await websocket.send(json.dumps(dateGramada))
        await asyncio.sleep(1)

start_server = websockets.serve(trimite_date, "localhost", 2323)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()