from model.bot import Bot

class BotController:
    def __init__(self):
        self.bot = Bot(train_mode=False)  

    def get_move(self, board):
        """
        Retourne le coup que le bot veut jouer en fonction du plateau actuel.
        """
        return self.bot.decide_move(board)

    def train_bot(self, games=1000, learning_rate=0.005):
        """
        Entraîne le bot et retourne True si réussi, False sinon.
        """
        try:
            self.bot.train(games=games, learning_rate=learning_rate)
            return True
        except Exception as e:
            print(f"Erreur lors de l'entraînement : {e}")
            return False
