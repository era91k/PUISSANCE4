from fastapi import APIRouter, HTTPException, Depends, Body
from app.model_game import Game
from app.utils import check_winner  # Fonction pour vérifier les conditions de victoire
from typing import List
from pymongo import MongoClient
import os

router = APIRouter()

# Configuration de la connexion à MongoDB
mongo_uri = os.getenv("MONGO_URI", "mongodb://mongo:27017")
client = MongoClient(mongo_uri)
db = client["user_db"]  # Assurez-vous d'utiliser la bonne base de données

# Stocker les jeux en mémoire (à remplacer par une base de données plus tard)
games: List[Game] = []

# Fonction pour jouer un coup
def drop_piece(board: List[List[int]], column: int, player_id: int) -> bool:
    """
    Insère un jeton dans la colonne spécifiée pour le joueur donné.
    Renvoie True si le coup a été joué avec succès, False sinon.
    """
    for row in reversed(board):  # Parcours de bas en haut pour trouver la première ligne libre
        if row[column] == 0:  # Si la cellule est vide (0)
            row[column] = player_id  # On place le jeton du joueur
            return True
    return False

# Route pour mettre à jour le score d'un utilisateur
@router.post("/update_score")
def update_score(name: str = Body(...), score: int = Body(...)):
    user_collection = db["users"]
    user = user_collection.find_one({"name": name})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    new_score = user.get("score", 0) + score
    user_collection.update_one({"name": name}, {"$set": {"score": new_score}})
    return {"name": name, "new_score": new_score}

# Route pour récupérer le score d'un utilisateur
@router.get("/get_score/{name}")
def get_score(name: str):
    user_collection = db["users"]
    user = user_collection.find_one({"name": name})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"name": name, "score": user.get("score", 0)}