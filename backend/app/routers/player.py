from fastapi import APIRouter
from app.models import Player
from typing import List

router = APIRouter()

# Stocker les joueurs en mémoire
players: List[Player] = []

# Route pour créer un joueur
@router.post("/", response_model=Player)
def create_player(player: Player):
    players.append(player)
    return player

# Route pour récupérer tous les joueurs
@router.get("/", response_model=List[Player])
def get_players():
    return players
