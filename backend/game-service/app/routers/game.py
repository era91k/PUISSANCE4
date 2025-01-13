from fastapi import APIRouter, HTTPException, Body
from app.model_game import Game
from app.utils import check_winner
from typing import List
from pymongo import MongoClient
import os
import logging
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
router_online = APIRouter()

mongo_uri = os.getenv("MONGO_URI", "mongodb://mongo:27017")
client = MongoClient(mongo_uri)
db = client["user_db"]

games: List[Game] = []
online_games = {}

class Move(BaseModel):
    column: int
    player_id: int

def drop_piece(board: List[List[int]], column: int, player_id: int) -> int:
    for row_index in range(len(board) - 1, -1, -1):
        if board[row_index][column] == 0:
            board[row_index][column] = player_id
            return row_index
    return -1

@router.get("/", response_model=List[Game])
def get_games():
    return games

@router.post("/", response_model=Game)
def create_game(game: Game):
    game.status = "active"
    games.append(game)
    logger.info(f"Game created with ID: {game.id}")
    return game

@router.delete("/{game_id}")
def delete_game(game_id: int):
    for game in games:
        if game.id == game_id:
            games.remove(game)
            return {"message": "Game deleted successfully"}
    raise HTTPException(status_code=404, detail="Game not found")

@router.put("/{game_id}")
def play_move(game_id: int, move: Move):
    for game in games:
        if game.id == game_id:
            if move.column < 0 or move.column >= len(game.board[0]):
                raise HTTPException(status_code=400, detail="Invalid column")

            row_index = drop_piece(game.board, move.column, move.player_id)
            if row_index == -1:
                raise HTTPException(status_code=400, detail="Column is full")

            if check_winner(game.board, move.player_id):
                game.status = "won"
                return {
                    "message": f"Player {move.player_id} wins!",
                    "board": game.board,
                    "status": game.status,
                    "id": game.id,
                    "row": row_index,
                    "player_id": move.player_id
                }

            if all(cell != 0 for row in game.board for cell in row):
                game.status = "draw"
                return {
                    "message": "The game is a draw!",
                    "board": game.board,
                    "status": game.status,
                    "id": game.id,
                    "row": row_index,
                    "player_id": move.player_id
                }

            game.current_turn = 2 if move.player_id == 1 else 1
            return {
                "message": f"Player {move.player_id} played in column {move.column}",
                "board": game.board,
                "status": game.status,
                "current_turn": game.current_turn,
                "row": row_index,
                "player_id": move.player_id
            }

    raise HTTPException(status_code=404, detail="Game not found")


@router_online.post("/")
def create_online_game(playerName: str = Body(...), gameCode: str = Body(...)):
    if gameCode in online_games:
        raise HTTPException(status_code=400, detail="Game code already exists.")

    # Check for duplicate player names in all online games
    if any(game["player1"] == playerName or game["player2"] == playerName for game in online_games.values()):
        raise HTTPException(status_code=400, detail="Player name is already in use.")

    online_games[gameCode] = {
        "player1": playerName,
        "player2": None,
        "board": [[0]*7 for _ in range(6)],
        "current_turn": 1,
        "status": "waiting"
    }
    return {"message": "Online game created successfully."}

@router_online.post("/join")
def join_online_game(playerName: str = Body(...), gameCode: str = Body(...)):
    if gameCode not in online_games:
        raise HTTPException(status_code=404, detail="Game not found.")

    game = online_games[gameCode]
    if game["player2"] is not None:
        raise HTTPException(status_code=400, detail="Game already has two players.")

    # Check for duplicate player names
    if playerName in [game["player1"], game["player2"]] or any(
        game["player1"] == playerName or game["player2"] == playerName for game in online_games.values()
    ):
        raise HTTPException(status_code=400, detail="Player name is already in use.")

    game["player2"] = playerName
    game["status"] = "ready"
    return {"message": "Joined game successfully.", "game": game}

@router_online.get("/{gameCode}")
def get_online_game_status(gameCode: str):
    if gameCode not in online_games:
        raise HTTPException(status_code=404, detail="Game not found.")
    return online_games[gameCode]

@router_online.put("/{gameCode}")
def play_online_move(gameCode: str, column: int, player_id: int):
    if gameCode not in online_games:
        raise HTTPException(status_code=404, detail="Game not found.")

    game = online_games[gameCode]
    if game["status"] not in ("waiting", "ready", "active"):
        raise HTTPException(status_code=400, detail="Game is not in a playable state.")

    if player_id not in [1, 2]:
        raise HTTPException(status_code=400, detail="Invalid player ID")

    if column < 0 or column >= 7:
        raise HTTPException(status_code=400, detail="Invalid column")

    row_index = drop_piece(game["board"], column, player_id)
    if row_index == -1:
        raise HTTPException(status_code=400, detail="Column is full")

    # Check for a winner
    if check_winner(game["board"], player_id):
        game["status"] = "won"
        game["winner_id"] = player_id  # Lock the winner
        return {
            "message": f"Player {player_id} wins!",
            "board": game["board"],
            "status": game["status"],
            "winner_id": player_id,  # Include winner ID in the response
            "row": row_index
        }

    # Check for a draw
    if all(cell != 0 for row in game["board"] for cell in row):
        game["status"] = "draw"
        return {
            "message": "The game is a draw!",
            "board": game["board"],
            "status": game["status"],
            "row": row_index
        }

    # Continue game
    game["current_turn"] = 2 if player_id == 1 else 1
    game["status"] = "active"
    return {
        "message": f"Player {player_id} played in column {column}",
        "board": game["board"],
        "status": game["status"],
        "current_turn": game["current_turn"],
        "row": row_index
    }


@router_online.patch("/{gameCode}")
def reset_online_game(gameCode: str):

    if gameCode not in online_games:
        raise HTTPException(status_code=404, detail="Game not found.")

    game = online_games[gameCode]

    # If we haven't stored 'next_start_player', or it's the first reset, default to 2.
    if "next_start_player" not in game:
        game["next_start_player"] = 2
    else:
        game["next_start_player"] = 1 if game["next_start_player"] == 2 else 2

    start = game["next_start_player"]

    game["board"] = [[0]*7 for _ in range(6)]
    if "winner_id" in game:
        del game["winner_id"]

    game["status"] = "active"
    game["current_turn"] = start

    return {
        "message": f"Game reset. Player {start} starts now.",
        "board": game["board"],
        "status": game["status"],
        "current_turn": start
    }

@router.post("/online/score")
def update_online_score(
    gameCode: str = Body(...),
    name: str = Body(...),
    score: int = Body(...)
):

    if gameCode not in online_games:
        raise HTTPException(status_code=404, detail="Game not found.")

    user_collection = db["users"]
    user = user_collection.find_one({"name": name})

    # If user doesn't exist, create it
    if not user:
        user_collection.insert_one({"name": name, "score": 0})
        user = user_collection.find_one({"name": name})

    new_score = user.get("score", 0) + score
    user_collection.update_one({"name": name}, {"$set": {"score": new_score}})

    return {"name": name, "new_score": new_score}

@router.delete("/online/{gameCode}")
def destroy_online_game(gameCode: str):

    if gameCode not in online_games:
        raise HTTPException(status_code=404, detail="Game not found.")

    del online_games[gameCode]
    return {"message": f"Game {gameCode} has been destroyed."}


