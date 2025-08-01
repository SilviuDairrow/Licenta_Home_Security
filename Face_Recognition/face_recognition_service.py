import os
import asyncio
import json
import base64
import cv2
import numpy as np
import websockets
import insightface
import requests

from datetime import datetime

Folder_Fete_Jupani = "Fete_Jupani_Detectate"
Folder_Fete_Straine = "Fete_Straine_Detectate"
SIMILARITY_THRESHOLD = 0.80

os.makedirs(Folder_Fete_Jupani, exist_ok=True)
os.makedirs(Folder_Fete_Straine, exist_ok=True)

detectie_fata = insightface.app.FaceAnalysis(providers=['CPUExecutionProvider'])
detectie_fata.prepare(ctx_id=-1)
detectie_fata.det_model.nms_thresh = 0.4

async def get_token(camera_id):

    uri = f"ws://nginx/ws/{camera_id}"

    try:
        async with websockets.connect(uri) as websocket:

            await websocket.send(f"face_recog_{camera_id}_token")

            while True:

                date = await websocket.recv()
                frame_date = json.loads(date)

                if frame_date.get("type") == "token":
                    return frame_date["token"]
                
    except Exception as e:
        print(f"Eroare cand vr sa iau tokenul pe {camera_id}: {e}")
        return None

def load_fete_jupani():

    embeddings_fete = []

    for nume_fila in os.listdir(Folder_Fete_Jupani):
        if nume_fila.lower().endswith(('.png', '.jpg', '.jpeg')):
            path_fila = os.path.join(Folder_Fete_Jupani, nume_fila)

            try:
                img = cv2.imread(path_fila)

                if img is None:
                    continue

                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                fete = detectie_fata.get(img_rgb)

                if fete:
                    embeddings_fete.append(fete[0].embedding)

            except Exception as eroare:
                print(f"Eroare la procesarea filei: {nume_fila}: {eroare}")

    return embeddings_fete

embeddings_fete = load_fete_jupani()

def similaritate_cosin(a, b):
    
    x = np.linalg.norm(a) * np.linalg.norm(b)
    return np.dot(a, b) / x

def is_fata_cunoscuta(embedding):

    for known in embeddings_fete:
        if similaritate_cosin(embedding, known) >= SIMILARITY_THRESHOLD:
            return True
        
    return False

async def upload_image_to_seaweed(camera_id, image_data, token):

    try:

        response = requests.post(
            f"http://server:8000/api/upload/?camera_id={camera_id}", 
            files={'file': ('image.jpg', image_data, 'image/jpeg')},
            headers={'Authorization': f'Bearer {token}'},
            timeout=5
        )

        if response.status_code == 200:
            print(f"Imagine incarcata cu succes: {response.json()}")

        else:
            print(f"Eroare la incarcarea imaginii: {response.text}")

    except Exception as e:
        print(f"Eroare la upload: {e}")

async def procesare_camera(camera_id):

    uri = f"ws://nginx/ws/{camera_id}"
    tip_client = f"face_recog_{camera_id}"

    token_task = asyncio.create_task(get_token(camera_id))
    headers = None

    while True:
        try:

            async with websockets.connect(uri) as websocket:

                print(f"Conectat la {camera_id}")
                await websocket.send(tip_client)

                while True:
                    try:

                        date = await websocket.recv()
                        frame_date = json.loads(date)

                        if camera_id in frame_date:

                            bytes_img = base64.b64decode(frame_date[camera_id])
                            np_arr = np.frombuffer(bytes_img, np.uint8)
                            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

                            if frame is None:
                                print(f"Eroare frame gol pe {camera_id}")
                                continue

                            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                            fete = detectie_fata.get(frame_rgb)

                            if not fete:
                                continue

                            if token_task.done():

                                token = await token_task

                                if token:
                                    headers = {'Authorization': f'Bearer {token}'}
                                    print("Token actualizat pt camerra", camera_id)

                                token_task = asyncio.create_task(get_token(camera_id))

                            for fata in fete:
                                
                                if not is_fata_cunoscuta(fata.embedding):
                                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                                    cale_fata = os.path.join(Folder_Fete_Straine, f"{timestamp}.jpg")
                                    
                                    try:
                                        cv2.imwrite(cale_fata, frame)
                                        print(f"Fata straina detectata si salvata: {cale_fata}")

                                        if headers:

                                            await upload_image_to_seaweed(camera_id, bytes_img, headers['Authorization'].split()[1])
                                            print(f"Fata este trimisa pt upload: {timestamp}.jpg")

                                        else:
                                            print("N am token valid deci upload anulat")

                                    except Exception as e:
                                        print(f"Eroare la salvarea/upload fata: {e}")

                    except Exception as e:
                        print(f"Eroare la procesarea frameului de pe {camera_id}: {e}")
                        break

        except Exception as e:
            print(f"S-a pierdut conex la {camera_id}: {e}. Recon in 3 sec")
            await asyncio.sleep(3)

async def reload_periodic_jupani(interval):
    global embeddings_fete

    while True:
        try:

            await asyncio.sleep(interval)

            new_embeddings = load_fete_jupani()

            if new_embeddings:
                embeddings_fete = new_embeddings
                print(f"Se reincarca imaginile jupanilor - {len(embeddings_fete)} fete jupani incarcate")

        except Exception as e:
            print(f"Eroare la reload fete jupani: {e}")

async def main():
    await asyncio.gather(
        procesare_camera("camera1"),
        procesare_camera("camera2"),
        reload_periodic_jupani(60) #sec
    )

if __name__ == "__main__":
    asyncio.run(main())