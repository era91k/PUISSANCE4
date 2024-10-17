import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Flask, request, jsonify
from controller.bot_controller import BotController

app = Flask(__name__)
bot_controller = BotController()

@app.route('/bot/move', methods=['POST'])
def get_bot_move():
    data = request.get_json()
    board = data.get('board', [])
    
    # Le bot calcule le coup à jouer
    move = bot_controller.get_move(board)
    
    return jsonify({"move": move}), 200 if move is not None else 400

@app.route('/bot/train', methods=['POST'])
def train_bot():
    data = request.get_json()
    games = data.get('games', 1000)  # Par défaut, entraîner sur 1000 parties
    learning_rate = data.get('learning_rate', 0.001)  # Taux d'apprentissage par défaut
    
    success = bot_controller.train_bot(games=games, learning_rate=learning_rate)
    if success:
        return jsonify({"message": "Bot entraîné avec succès"}), 200
    return jsonify({"message": "Échec de l'entraînement du bot"}), 500

if __name__ == '__main__':
    app.run(debug=True)
