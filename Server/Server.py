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
    allow_origins=["http://localhost:8000", "http://localhost:8001"], 
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

@app.get("/Dashboard")
def get_dashboard(user_curent: str = Depends(get_user_curent)):
    
    dashboard_path = Path("./html/Dashboard.html")
    
    if dashboard_path.exists():
        
        with open(dashboard_path, "r", encoding="utf-8") as fila:
            content = fila.read()
            
        return HTMLResponse(content=content)
    
    raise HTTPException(status_code=404, detail="Dashboard.html nu exista")

