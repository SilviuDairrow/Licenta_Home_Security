from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import jwt
import json
from datetime import datetime, timedelta
from Models import User, Token
from Database import creere_user, cautare_user, verif_parola, creere_table

app = FastAPI()

algoritm_criptare = "HS512"
cheie = "bruh"
timp_pt_expirare = 999999

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    creere_table()

def creere_token(data: dict, timp_expirare: timedelta = timedelta(minutes=timp_pt_expirare)):

    pt_encode = data.copy()
    expira = datetime.utcnow() + timp_expirare

    pt_encode.update({"exp": expira})
    encode_jwt = jwt.encode(pt_encode, cheie, algorithm=algoritm_criptare)

    return encode_jwt

@app.post("/Login")
def post_login(input_user: User):

    user = cautare_user(input_user.id)

    if user and verif_parola(input_user.password, user["password"]):
            
            token = creere_token(data={"sub": user["username"]})
            return {"status": "success", "access_token": token, "tip_token": "bearer"}
    
    raise HTTPException(status_code=401, detail="Login incorect")

@app.get("/Login")
def get_login():

    return JSONResponse(content={"message": "Nu merge get pe path asta"})

@app.post("/creeaza_cont")
def creeaza_cont(input_user: User):
     
     rez = creere_user(input_user.id, input_user.password)

     if "Eroare" in rez:
          raise HTTPException(status_code=400, detail="Exista deja un cont cu acest username")
     
     return {"status": "success", "message": "Contul a fost creeat cu succes"}