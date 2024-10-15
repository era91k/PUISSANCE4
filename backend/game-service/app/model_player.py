# player.py
from pydantic import BaseModel

# Modèle pour un joueur
class Player(BaseModel):
    id: int
    name: str