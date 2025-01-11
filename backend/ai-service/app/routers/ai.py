from fastapi import APIRouter, HTTPException, Body, Query
from typing import List, Tuple
import time
import math
import random

router = APIRouter()

# Constants for players
EMPTY = 0
PLAYER_AI = 2
PLAYER_HUMAN = 1

def evaluate_window(window: List[int], player: int) -> int:
    """
    Evaluate a window of 4 slots for scoring.
    """
    score = 0
    opponent = PLAYER_HUMAN if player == PLAYER_AI else PLAYER_AI

    if window.count(player) == 4:
        score += 100
    elif window.count(player) == 3 and window.count(EMPTY) == 1:
        score += 5
    elif window.count(player) == 2 and window.count(EMPTY) == 2:
        score += 2

    if window.count(opponent) == 3 and window.count(EMPTY) == 1:
        score -= 4  # Block the opponent's potential win

    return score

def score_position(board: List[List[int]], player: int) -> int:
    """
    Score the current board for the given player.
    """
    score = 0
    rows, cols = len(board), len(board[0])

    # Score center column
    center_col = [board[row][cols // 2] for row in range(rows)]
    score += center_col.count(player) * 3

    # Score horizontal
    for row in board:
        for col in range(cols - 3):
            window = row[col:col + 4]
            score += evaluate_window(window, player)

    # Score vertical
    for col in range(cols):
        for row in range(rows - 3):
            window = [board[row + i][col] for i in range(4)]
            score += evaluate_window(window, player)

    # Score positive diagonal
    for row in range(rows - 3):
        for col in range(cols - 3):
            window = [board[row + i][col + i] for i in range(4)]
            score += evaluate_window(window, player)

    # Score negative diagonal
    for row in range(rows - 3):
        for col in range(3, cols):
            window = [board[row + i][col - i] for i in range(4)]
            score += evaluate_window(window, player)

    return score

def is_valid_location(board: List[List[int]], col: int) -> bool:
    """
    Check if a column is valid for a move.
    """
    return board[0][col] == EMPTY

def get_valid_columns(board: List[List[int]]) -> List[int]:
    """
    Get all valid columns for a move.
    """
    return [col for col in range(len(board[0])) if is_valid_location(board, col)]

def drop_piece(board: List[List[int]], row: int, col: int, piece: int):
    """
    Drop a piece in the board at the specified location.
    """
    board[row][col] = piece

def get_next_open_row(board: List[List[int]], col: int) -> int:
    """
    Get the next open row in a column.
    """
    for row in range(len(board) - 1, -1, -1):
        if board[row][col] == EMPTY:
            return row

def winning_move(board: List[List[int]], piece: int) -> bool:
    """
    Check if the given piece has a winning move.
    """
    rows, cols = len(board), len(board[0])

    # Check horizontal locations
    for row in range(rows):
        for col in range(cols - 3):
            if all(board[row][col + i] == piece for i in range(4)):
                return True

    # Check vertical locations
    for col in range(cols):
        for row in range(rows - 3):
            if all(board[row + i][col] == piece for i in range(4)):
                return True

    # Check positive diagonals
    for row in range(rows - 3):
        for col in range(cols - 3):
            if all(board[row + i][col + i] == piece for i in range(4)):
                return True

    # Check negative diagonals
    for row in range(rows - 3):
        for col in range(3, cols):
            if all(board[row + i][col - i] == piece for i in range(4)):
                return True

    return False

def minimax(board: List[List[int]], depth: int, alpha: float, beta: float, maximizingPlayer: bool) -> Tuple[int, int]:
    """
    Minimax algorithm with alpha-beta pruning.
    """
    valid_columns = get_valid_columns(board)
    is_terminal = winning_move(board, PLAYER_AI) or winning_move(board, PLAYER_HUMAN) or not valid_columns

    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, PLAYER_AI):
                return (None, 100000000000000)
            elif winning_move(board, PLAYER_HUMAN):
                return (None, -10000000000000)
            else:  # No valid moves (draw)
                return (None, 0)
        else:  # Depth is zero
            return (None, score_position(board, PLAYER_AI))

    if maximizingPlayer:
        value = -math.inf
        best_col = random.choice(valid_columns)
        for col in valid_columns:
            row = get_next_open_row(board, col)
            temp_board = [row.copy() for row in board]
            drop_piece(temp_board, row, col, PLAYER_AI)
            new_score = minimax(temp_board, depth - 1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                best_col = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return best_col, value

    else:  # Minimizing player
        value = math.inf
        best_col = random.choice(valid_columns)
        for col in valid_columns:
            row = get_next_open_row(board, col)
            temp_board = [row.copy() for row in board]
            drop_piece(temp_board, row, col, PLAYER_HUMAN)
            new_score = minimax(temp_board, depth - 1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                best_col = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return best_col, value

@router.post("/move")
def get_ai_move(board: List[List[int]] = Body(...), difficulty: str = Query("medium")):
    """
    AI endpoint using Minimax algorithm with difficulty levels.
    """
    start_time = time.time()
    valid_columns = get_valid_columns(board)
    if not valid_columns:
        raise HTTPException(status_code=400, detail="No valid moves available")
    
    # Set depth based on difficulty
    if difficulty == "easy":
        depth = 1  # Réduire la profondeur à 1 pour rendre l'IA moins performante
    elif difficulty == "medium":
        depth = 4
    elif difficulty == "hard":
        depth = 6
    else:
        raise HTTPException(status_code=400, detail="Invalid difficulty level")

    # Introduire un élément de hasard en mode facile
    if difficulty == "easy" and random.random() < 0.5:
        col = random.choice(valid_columns)
    else:
        col, _ = minimax(board, depth=depth, alpha=-math.inf, beta=math.inf, maximizingPlayer=True)
    
    end_time = time.time()

    print(f"AI selected column {col} in {end_time - start_time:.2f}s with difficulty {difficulty}")
    time.sleep(1)  # Simulate AI thinking time
    return {"column": col}