import sys
import os
import requests  # Module pour faire des requêtes HTTP
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from game import Game  # Assure-toi que cette importation est correcte et que le fichier `game.py` existe

# URL de l'API Flask
API_URL = "http://127.0.0.1:5000/bot/move"

if __name__ == "__main__":
    game = Game()

    # Partie en local où tu joues contre le bot via l'API
    while not game.is_over():
        game.display_board()

        # Tour de l'utilisateur
        user_move = int(input("Entrez votre coup (0-6) : "))
        game.place_piece(user_move, 1)  # 1 représente l'utilisateur

        if game.is_over():
            break

        # Tour du bot (via l'API)
        response = requests.post(API_URL, json={"board": game.board})
        if response.status_code == 200:
            bot_move = response.json().get("move")
            print(f"Le bot joue dans la colonne : {bot_move}")
            game.place_piece(bot_move, 2)  # 2 représente le bot
        else:
            print("Erreur lors de l'appel à l'API du bot :", response.text)
            break

    print("Partie terminée !")
    game.display_board()
