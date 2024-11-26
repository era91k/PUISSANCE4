from fastapi import APIRouter, HTTPException, Body
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
def drop_piece(board: List[List[int]], column: int, player_id: int) -> int:
    """
    Insère un jeton dans la colonne spécifiée pour le joueur donné.
    Renvoie l'index de la ligne où le jeton a été placé.
    """
    for row_index in range(len(board) - 1, -1, -1):  # Parcours de bas en haut
        if board[row_index][column] == 0:  # Si la cellule est vide (0)
            board[row_index][column] = player_id  # Place le jeton du joueur
            return row_index  # Retourne le numéro de la ligne où le jeton a été placé
    return -1  # Si la colonne est pleine

# Route pour créer une nouvelle partie
@router.post("/", response_model=Game)
def create_game(game: Game):
    game.status = "active"  # Initialiser le statut à "active"
    games.append(game)
    return game

# Route pour jouer un coup
@router.put("/{game_id}/play")
def play_move(game_id: int, column: int, player_id: int):
    # Trouver la partie en fonction de son ID
    for game in games:
        if game.id == game_id:
            if column < 0 or column >= len(game.board[0]):
                raise HTTPException(status_code=400, detail="Colonne invalide")
            
            row_index = drop_piece(game.board, column, player_id)
            if row_index == -1:
                raise HTTPException(status_code=400, detail="Colonne pleine")

            # Vérification du gagnant après le coup
            if check_winner(game.board, player_id):
                game.status = "won"
                return {"message": f"Player {player_id} wins!", "board": game.board, "status": game.status, "id": game.id, "row": row_index}

            # Vérification si la partie est un match nul
            if all(cell != 0 for row in game.board for cell in row):  # Si toutes les cases sont remplies
                game.status = "draw"
                return {"message": "The game is a draw!", "board": game.board, "status": game.status, "id": game.id, "row": row_index}
            
            # Passer au tour du joueur suivant
            game.current_turn = 2 if player_id == 1 else 1
            return {"message": f"Player {player_id} played in column {column}", "board": game.board, "status": game.status, "current_turn": game.current_turn, "row": row_index}
    
    raise HTTPException(status_code=404, detail="Game not found")

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