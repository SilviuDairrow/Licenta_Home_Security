from fastapi import Depends, FastAPI, HTTPException, Request, Response, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware

import datetime
import asyncio
import jwt
import base64
import json

from pydantic import BaseModel

from pathlib import Path


app = FastAPI()
ultimul_frame = {"camera1": None, "camera2": None}

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
    except ValueError:
        raise HTTPException(status_code=401, detail="Headerul tokenului nu are formatul corect")

    user = get_user_curent(token)

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

        elif tip_client == "face_recog_camera1":
            while True:

                if ultimul_frame[camera_id]:
                    await websocket.send_text(json.dumps({camera_id: base64.b64encode(ultimul_frame[camera_id]).decode('utf-8')}))
                
                await asyncio.sleep(0.1)
        
        elif tip_client == "face_recog_camera2":
            while True:

                if ultimul_frame[camera_id]:
                    await websocket.send_text(json.dumps({camera_id: base64.b64encode(ultimul_frame[camera_id]).decode('utf-8')}))
                
                await asyncio.sleep(0.1)
                
    except WebSocketDisconnect:
        print(f"Clientul {tip_client} de la camera {camera_id} a fost deconectat")