from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware

import datetime
from pydantic import BaseModel
import jwt
from pathlib import Path

app = FastAPI()

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

