from urllib.parse import quote_plus
from fastapi import Depends, FastAPI, HTTPException, Request, Response, WebSocket, WebSocketDisconnect
from fastapi import UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware

import datetime
import asyncio
import jwt
import base64
import json
import requests

from pydantic import BaseModel
from pymongo import MongoClient

from pathlib import Path

app = FastAPI()
ultimul_frame = {"camera1": None, "camera2": None}
tokenuri_active = {}

oauth2 = OAuth2PasswordBearer(tokenUrl="token")
algoritm_criptare = "HS512"
cheie = "bruh"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = MongoClient("mongodb://mongo-server:27017/")
db = client["db_poze_useri"]
colectie_useri = db["users"]

seaweed_master_URL = "http://master:9333/"
seaweed_URL = "http://volume:8083/"

def creere_url(fid): return f"http://localhost:8083/{quote_plus(fid)}.jpg?width=200&height=200"

def get_user_curent(token: str = Depends(oauth2)):

    try:
        data = jwt.decode(token, cheie, algorithms=[algoritm_criptare]) 
        username: str = data.get("sub")

        if username is None:
            raise HTTPException(status_code=401, detail="Token Invalid de la login: nu exista 'sub'")
        return username
    
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token invalid")
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Tokenul de login a expriat, relogin!")

@app.get("/Dashboard")
def get_dashboard(request: Request,):

    token = request.headers.get("Authorization")

    if not token:
        raise HTTPException(status_code=401, detail="Nu exista headerul tokenului")
    

    try:
        _, token = token.split()
        user = get_user_curent(token)

        tokenuri_active["camera1"] = token
        tokenuri_active["camera2"] = token

    except ValueError:
        raise HTTPException(status_code=401, detail="Headerul tokenului nu are formatul corect")

    return {
        "status": "success",
        "message": "Te-ai logat cu succes",
        "user": user,
    }

@app.websocket("/ws/{camera_id}")
async def websocket_camere(websocket: WebSocket, camera_id: str):

    await websocket.accept()
    
    tip_client = await websocket.receive_text()

    try:
        if tip_client == "camera1":
            while True:

                data = await websocket.receive_text()

                date_frame = json.loads(data)

                if camera_id in date_frame:
                    ultimul_frame[camera_id] = base64.b64decode(date_frame[camera_id])

                await asyncio.sleep(0.1)

        elif tip_client == "camera2":
            while True:

                data = await websocket.receive_text()

                date_frame = json.loads(data)

                if camera_id in date_frame:
                    ultimul_frame[camera_id] = base64.b64decode(date_frame[camera_id])

                await asyncio.sleep(0.1)

        elif tip_client == "frontend":
            while True:

                if ultimul_frame[camera_id]:
                    await websocket.send_text(json.dumps({camera_id: base64.b64encode(ultimul_frame[camera_id]).decode('utf-8')}))

                await asyncio.sleep(0.1)

        elif tip_client == f"face_recog_{camera_id}":
            while True:

                if ultimul_frame[camera_id]:
                    await websocket.send_text(json.dumps({camera_id: base64.b64encode(ultimul_frame[camera_id]).decode('utf-8')}))
                
                await asyncio.sleep(0.1)
        
        elif tip_client == f"face_recog_{camera_id}_token":
            while True:

                if camera_id in tokenuri_active:

                    await websocket.send_text(json.dumps({
                        "type": "token",
                        "token": tokenuri_active[camera_id]
                    }))

                await asyncio.sleep(5)
                
    except WebSocketDisconnect:
        print(f"Clientul {tip_client} de la camera {camera_id} a fost deconectat")


@app.get("/api/{username}/ImaginiStraini")
def get_imagini_straini(username: str, user_curent = Depends(get_user_curent)):

    if username != user_curent:
        raise HTTPException(status_code=403, detail="Acces interzis aici!")
    
    user = colectie_useri.find_one({"username": username})

    if not user:
        raise HTTPException(status_code=404, detail="Nu s-a gasit user-ul")
    
    camera1_fids = [fid for fid in user.get("camera1_fids", [])]
    camera2_fids = [fid for fid in user.get("camera2_fids", [])]

    return {"ImaginiStraini": {"camera1": camera1_fids, "camera2": camera2_fids}}

@app.get("/api/{username}/ImaginiJupani")
def get_imagini_jupani(username: str, user_curent = Depends(get_user_curent)):

    if username != user_curent:
        raise HTTPException(status_code=403, detail="Acces interzis aici!")
    
    user = colectie_useri.find_one({"username": username})

    if not user:
        raise HTTPException(status_code=404, detail="Nu s-a gasit user-ul")
    
    jupan_fids = set(user.get("jupan_fids",[]))

    return {"ImaginiJupani": jupan_fids}

@app.post("/api/{username}/DevineJupan")
def devine_jupan(username: str, fid: str, user_curent: str = Depends(get_user_curent)):

    if username != user_curent:
        raise HTTPException(status_code=403, detail="Acces interzis aici!")
    
    user = colectie_useri.find_one({"username": username})

    if not user:
        raise HTTPException(status_code=404, detail="Nu s-a gasit user-ul")

    colectie_useri.update_one(
        {"username": username},
        {"$pull": {"camera1_fids": fid, "camera2_fids": fid},
         "$addToSet": {"jupan_fids": fid}}
    )

    return {"message": "A fost adaugata imaginea la sectiunea Jupani"}

@app.post("/api/upload/")
async def upload_imagine(
    camera_id: str,
    file: UploadFile = File(...),
    user_curent: str = Depends(get_user_curent)
):
    try:
        fid_raspuns = requests.get(f"{seaweed_master_URL}dir/assign")
        if fid_raspuns.status_code != 200:
            raise HTTPException(status_code=500, detail="Nu a mers creearea unui FID de catre Master Seaweed")

        fid_data = fid_raspuns.json()
        fid = fid_data.get("fid")
        url_volum = fid_data.get("publicUrl")

        if not fid or not url_volum:
            raise HTTPException(status_code=500, detail="Raspuns invalid de la Seaweed")

        continut = await file.read()
        files = {'file': ('image.jpg', continut, file.content_type)}
        raspuns_upload = requests.post(f"http://{url_volum}/{fid}", files=files)

        if raspuns_upload.status_code != 201:
            raise HTTPException(status_code=500, detail="Eroare la upload in Seaweed")

        user = colectie_useri.find_one({"username": user_curent})
        if not user:
            colectie_useri.insert_one({"username": user_curent, "camera1_fids": [], "camera2_fids": []})

        colectie_useri.update_one(
            {"username": user_curent},
            {"$push": {f"{camera_id}_fids": fid}}
        )

        return {"message": "Imagine uploadata cu succes", "fid": fid}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Eroare la upload: {e}")

@app.delete("/api/{username}/delete/{fid}")
def delete_imagine(username: str, fid: str, user_curent: str = Depends(get_user_curent)):

    if username != user_curent:
        raise HTTPException(status_code=403, detail="Acces interzis aici!")
    
    user = colectie_useri.find_one({"username": username})

    if not user:
        raise HTTPException(status_code=404, detail="NU s-a gasit user-ul")
    
    colectie_useri.update_one(
        {"username": username},
        {"$pull": {"camera1_fids": fid, "camera2_fids": fid, "jupan_fids": fid}}
    )

    delete_imagine_sw = f"{seaweed_URL}/delete/{fid}"
    rasp = Request.delete(delete_imagine_sw)

    if rasp.status_code != 200:
        raise HTTPException(status_code=500, detail="Eroare la stergerea pozei din vollumele Seaweed")
    
    return {"message": "Imagine stearsa cu succes"}

@app.get("/api/{username}/ImaginiToate")
def get_imagini_toate(username: str, user: str = Depends(get_user_curent)):
    if username != user:
        raise HTTPException(status_code=403, detail="Acces interzis aici!")
    
    userul = colectie_useri.find_one({"username": username})

    if not userul:
        raise HTTPException(status_code=404, detail="User-ul nu exista!")
    
    camera1 = userul.get("camera1_fids", [])
    camera2 = userul.get("camera2_fids", [])

    camera_toate = list(set(camera1 + camera2))

    jupani = userul.get("jupan_fids", [])


    return{
        "straini": [creere_url(fid) for fid in camera_toate],
        "jupani": [creere_url(fid) for fid in jupani]
    }

