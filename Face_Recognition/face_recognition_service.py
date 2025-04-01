import os
import asyncio
import json
import base64
from datetime import datetime

import cv2
import numpy as np
import websockets
from PIL import Image
import insightface

#link pt modelele pe care le am folosit ca sa nu uit sa citez:
#https://github.com/deepinsight/insightface/releases/download/v0.7/buffalo_s.zip   

#git commit -m "Am adaugat face recognition cu insightface (delay total ~4-5sec), se stocheaza fetele necunoscute"

Folder_Fete_Jupani = "Fete_Jupani_Detectate"
Folder_Fete_Straini = "Fete_Straine_Detectate"

SIMILARITY_THRESHOLD = 0.80 

os.makedirs(Folder_Fete_Jupani, exist_ok=True)
os.makedirs(Folder_Fete_Straini, exist_ok=True)

detectie_fata = insightface.app.FaceAnalysis(providers=['CPUExecutionProvider'])
detectie_fata.prepare(ctx_id=-1)
detectie_fata.det_model.nms_thresh = 0.4

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
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def is_fata_cunoscuta(embedding):

    for known in embeddings_fete:
        if similaritate_cosin(embedding, known) >= SIMILARITY_THRESHOLD:
            return True
        
    return False

async def procesare_camera(camera_id):

    uri = f"ws://nginx/ws/{camera_id}"

    tip_client = f"face_recog_{camera_id}"

    while True:
        try:
            async with websockets.connect(uri) as websocket:

                print(f"Connected to {camera_id}")
                await websocket.send(tip_client)

                while True:
                    try:

                        date = await websocket.recv()
                        frame_date = json.loads(date)

                        if camera_id in frame_date:

                            img_bytes = base64.b64decode(frame_date[camera_id])

                            np_arr = np.frombuffer(img_bytes, np.uint8)
                            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

                            if frame is None:
                                continue

                            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                            fete = detectie_fata.get(frame_rgb)

                            for fata in fete:
                                if not is_fata_cunoscuta(fata.embedding):

                                    save_folder = os.path.join(Folder_Fete_Straini, camera_id)
                                    os.makedirs(save_folder, exist_ok=True)

                                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                                    nume_fila = os.path.join(save_folder, f"{timestamp}.jpg")

                                    cv2.imwrite(nume_fila, frame)
                                    print(f"Fata straina salvata: {nume_fila}")

                    except Exception as e:
                        print(f"Eroare la procesarea frameului de pe {camera_id}: {e}")
                        break

        except Exception as e:
            print(f"S-a pierdut conex la {camera_id}: {e}. Reconectare in 3 sec")
            await asyncio.sleep(3)

async def main():
    await asyncio.gather(
        procesare_camera("camera1"),
        procesare_camera("camera2")
    )

if __name__ == "__main__":
    asyncio.run(main())
