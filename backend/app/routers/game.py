from fastapi import APIRouter, HTTPException
from app.models import Game
from typing import List

router = APIRouter()

# Stocker les jeux en mémoire
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
    return False  # Si la colonne est pleine

# Route pour créer une nouvelle partie
@router.post("/", response_model=Game)
def create_game(game: Game):
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
            
            if not drop_piece(game.board, column, player_id):
                raise HTTPException(status_code=400, detail="Colonne pleine")
            
            return {"message": f"Player {player_id} played in column {column} for game {game_id}", "board": game.board}
    
    raise HTTPException(status_code=404, detail="Game not found")

# Route pour récupérer l'état d'une partie
@router.get("/{game_id}")
def get_game(game_id: int):
    for game in games:
        if game.id == game_id:
            return game
    raise HTTPException(status_code=404, detail="Game not found")
