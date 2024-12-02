from fastapi import APIRouter, HTTPException, Body
from typing import List
import random
import time

router = APIRouter()

@router.post("/move")
def get_ai_move(board: List[List[int]] = Body(...)):
    """
    Renvoie une colonne aléatoire valide pour le mouvement de l'IA.
    """
    valid_columns = [col for col in range(len(board[0])) if board[0][col] == 0]
    if not valid_columns:
        raise HTTPException(status_code=400, detail="No valid moves available")
    
    ai_move = random.choice(valid_columns)
    time.sleep(2)
    return {"column": ai_move}