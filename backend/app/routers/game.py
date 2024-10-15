from fastapi import APIRouter, HTTPException
from app.model_game import Game
from app.utils import check_winner  # Fonction pour vérifier les conditions de victoire
from typing import List

router = APIRouter()

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
    return False  # Si la colonne est pleine

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
            
            if not drop_piece(game.board, column, player_id):
                raise HTTPException(status_code=400, detail="Colonne pleine")

            # Vérification du gagnant après le coup
            if check_winner(game.board, player_id):
                game.status = "won"
                return {"message": f"Player {player_id} wins!", "board": game.board, "status": game.status, "id": game.id}

            # Vérification si la partie est un match nul
            if all(row[0] != 0 for row in game.board):  # Si toutes les cases de la première colonne sont remplies
                game.status = "draw"
                return {"message": "The game is a draw!", "board": game.board, "status": game.status, "id": game.id}
            
            # Passer au tour du joueur suivant
            game.current_turn = 2 if player_id == 1 else 1
            return {"message": f"Player {player_id} played in column {column} for game {game_id}", "board": game.board, "status": game.status, "id": game.id}
    
    raise HTTPException(status_code=404, detail="Game not found")


# Route pour récupérer l'état d'une partie
@router.get("/{game_id}")
def get_game(game_id: int):
    for game in games:
        if game.id == game_id:
            return game
    raise HTTPException(status_code=404, detail="Game not found")
