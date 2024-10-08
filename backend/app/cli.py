import requests

BASE_URL = "http://127.0.0.1:8000"  # URL de votre serveur FastAPI

def create_game():
    game_data = {
        "id": 1,
        "players": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}],
        "current_turn": 1,
        "board": [[0] * 7 for _ in range(6)]  # Plateau vide
    }
    response = requests.post(f"{BASE_URL}/game/", json=game_data)
    if response.status_code == 200:
        print("Game created successfully!")
    else:
        print("Failed to create game:", response.json())
    return game_data

def print_board(board):
    for row in board:
        print(" | ".join(str(x) if x != 0 else "." for x in row))
        print("-" * 29)  # Ligne de séparation

def play_move(game_id, column, player_id):
    response = requests.put(f"{BASE_URL}/game/{game_id}/play?column={column}&player_id={player_id}")
    if response.status_code == 200:
        print("Move played successfully!")
    else:
        print("Failed to play move:", response.json())

def get_game_state(game_id):
    response = requests.get(f"{BASE_URL}/game/{game_id}")
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to get game state:", response.json())
        return None

def main():
    game_data = create_game()
    while True:
        print_board(game_data["board"])
        
        current_turn = game_data["current_turn"]
        column = int(input(f"Player {current_turn}, enter the column (0-6) to drop your piece: "))
        
        play_move(game_data["id"], column, current_turn)
        
        game_state = get_game_state(game_data["id"])
        if game_state:
            game_data = game_state
        
        # Switch turn (simple)
        game_data["current_turn"] = 2 if current_turn == 1 else 1

if __name__ == "__main__":
    main()
