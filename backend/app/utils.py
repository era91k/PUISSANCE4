from typing import List

def check_winner(board: List[List[int]], player_id: int) -> bool:
    # Vérifier les lignes
    for row in board:
        for col in range(len(row) - 3):
            if row[col] == player_id and row[col + 1] == player_id and row[col + 2] == player_id and row[col + 3] == player_id:
                return True

    # Vérifier les colonnes
    for col in range(len(board[0])):
        for row in range(len(board) - 3):
            if board[row][col] == player_id and board[row + 1][col] == player_id and board[row + 2][col] == player_id and board[row + 3][col] == player_id:
                return True

    # Vérifier diagonales montantes
    for row in range(3, len(board)):
        for col in range(len(board[0]) - 3):
            if board[row][col] == player_id and board[row - 1][col + 1] == player_id and board[row - 2][col + 2] == player_id and board[row - 3][col + 3] == player_id:
                return True

    # Vérifier diagonales descendantes
    for row in range(len(board) - 3):
        for col in range(len(board[0]) - 3):
            if board[row][col] == player_id and board[row + 1][col + 1] == player_id and board[row + 2][col + 2] == player_id and board[row + 3][col + 3] == player_id:
                return True

    return False
