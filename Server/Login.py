from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

import jwt
import json

from datetime import datetime, timedelta

from Models import User, Token

app = FastAPI()

algoritm_criptare = "HS512"
cheie = "bruh"
timp_pt_expirare = 120


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://localhost:8001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


user_db = "./test_db/users.json"

app.mount("/static", StaticFiles(directory="./html"), name="static")

def load_useri():
    with open(user_db, "r") as file:
        data = json.load(file)
        return [User(**user) for user in data["users"]]

def creere_token(data: dict, timp_expirare: timedelta = timedelta(minutes=timp_pt_expirare)):

    pt_encode = data.copy()

    expira = datetime.utcnow() + timp_expirare

    pt_encode.update({"exp": expira})
    encode_jwt = jwt.encode(pt_encode, cheie, algorithm=algoritm_criptare )

    return encode_jwt

@app.post("/Login")
def post_login(input_user: User):

    useri = load_useri()

    for user in useri:
        if input_user.id == user.id and input_user.password == user.password:

            token = creere_token(data={"sub": user.id})
            return {"status": "success", "access_token": token, "tip_token": "bearer"}
    
    raise HTTPException(status_code=401, detail="Login incorect")

@app.get("/Login")
def get_login():
    
    with open("./html/Login.html", "r") as fila:
        return HTMLResponse(content=fila.read())