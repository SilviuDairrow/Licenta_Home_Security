from pymongo import MongoClient
import bcrypt
from typing import Optional


client = MongoClient("mongodb://mongo:27017/")
db = client["home_security"]
colectie_useri = db["credentiale_useri"]


def hash_parola(password: str) -> str:

    salt = bcrypt.gensalt()
    hash_password = bcrypt.hashpw(password.encode("utf-8"), salt)

    return hash_password.decode("utf-8")

def creere_table():
    if "credentiale_useri" not in db.list_collection_names():
        print("Se creeaza colectia 'credentiale_useri'")
        db.create_collection("credentiale_useri")
    else:
        print("Exista deja colectia")

def verif_parola(parola: str, hash_parola: str) -> bool:
    return bcrypt.checkpw(parola.encode("utf-8"), hash_parola.encode("utf-8"))

def cautare_user(username: str) -> Optional[dict]:
    return colectie_useri.find_one({"username": username})

def creere_user(username: str, password: str) -> str:

    if cautare_user(username):
        return "Eroare, exista user cu acest nume deja"
    
    hash_password = hash_parola(password)

    user = {"username": username, "password": hash_password}

    rez = colectie_useri.insert_one(user)
    return f"Succes, User-ul '{username}' a fost creeat cu ID-ul: {rez.inserted_id}"

def delete_user(username: str) -> bool:

    rez = colectie_useri.delete_one({"username": username})

    return rez.deleted_count > 0

def update_user(username: str, parola_noua: str) -> bool:
    
    hash_parola_noua = hash_parola(parola_noua)

    rez = colectie_useri.update_one(
        {"username": username},
        {"$set": {"password": hash_parola_noua}}
    )

    return rez.modified_count > 0