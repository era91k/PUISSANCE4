import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np


class BotAI(nn.Module):
    """
    Réseau neuronal pour le bot de Puissance 4.
    """
    def __init__(self):
        super(BotAI, self).__init__()
        self.model = nn.Sequential(
            nn.Flatten(),
            nn.Linear(7 * 6, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 7),  # 7 sorties pour chaque colonne
            nn.Softmax(dim=-1)
        )

    def forward(self, board):
        return self.model(board)


class Bot:
    def __init__(self, model_path="bot_model.pth", train_mode=True):
        """
        Initialise le bot, soit pour jouer avec un modèle pré-entraîné,
        soit pour l'entraîner si `train_mode` est activé.
        """
        self.ai = BotAI()
        self.model_path = model_path
        self.train_mode = train_mode
        if not train_mode:
            try:
                self.ai.load_state_dict(torch.load(model_path))
                self.ai.eval()  # Mode évaluation
                print("Modèle chargé avec succès.")
            except FileNotFoundError:
                print("Aucun modèle trouvé. Entraînez le bot avant de l'utiliser.")

    def decide_move(self, board):
        """
        Décide du coup à jouer en fonction de l'état du plateau.
        """
        board_tensor = torch.tensor(board, dtype=torch.float32).unsqueeze(0)
        with torch.no_grad():
            probabilities = self.ai(board_tensor).squeeze().numpy()

        # Choisir la colonne avec la plus grande probabilité
        available_columns = [i for i in range(len(board[0])) if board[0][i] == 0]
        best_move = max(available_columns, key=lambda x: probabilities[x]) if available_columns else None
        return best_move

    def train(self, games=1000, learning_rate=0.001, gamma=0.95):
        """
        Entraîne le bot en jouant des parties contre lui-même.
        """
        optimizer = optim.Adam(self.ai.parameters(), lr=learning_rate)
        criterion = nn.MSELoss()

        for game in range(games):
            board = np.zeros((6, 7))  # Plateau vide
            moves = []
            winner = None

            for turn in range(42):  # Jusqu'à 42 coups
                player = 1 if turn % 2 == 0 else 2

                # Décision du mouvement avec exploration
                move = self._decide_or_explore_move(board, player)
                if move is not None:
                    board[self._get_row(board, move)][move] = player
                    moves.append((board.copy(), move, player))

                # Vérifie s'il y a un gagnant
                winner = self._check_winner(board)
                if winner:
                    break

            # Calcul des récompenses et mise à jour du modèle
            self._train_on_game(moves, winner, optimizer, criterion, gamma)

        torch.save(self.ai.state_dict(), self.model_path)
        print("Modèle entraîné et sauvegardé.")

    def _decide_or_explore_move(self, board, player, exploration_rate=0.1):
        """
        Décide d'un coup soit en explorant, soit en exploitant le modèle.
        """
        if np.random.rand() < exploration_rate:
            return self._simulate_move(board, player)  # Mouvement aléatoire (exploration)
        else:
            board_tensor = torch.tensor(board, dtype=torch.float32).unsqueeze(0)
            with torch.no_grad():
                probabilities = self.ai(board_tensor).squeeze().numpy()
            available_columns = [i for i in range(len(board[0])) if board[0][i] == 0]
            return max(available_columns, key=lambda x: probabilities[x]) if available_columns else None

    def _train_on_game(self, moves, winner, optimizer, criterion, gamma):
        """
        Récompense les coups joués pendant une partie et rétropropagation.
        """
        reward = 1 if winner == 1 else -1 if winner == 2 else 0
        cumulative_reward = reward

        for board, move, player in reversed(moves):  # Régression temporelle inverse
            target = np.zeros(7)
            target[move] = cumulative_reward if player == winner else -cumulative_reward
            board_tensor = torch.tensor(board, dtype=torch.float32).unsqueeze(0)
            target_tensor = torch.tensor(target, dtype=torch.float32).unsqueeze(0)

            optimizer.zero_grad()
            output = self.ai(board_tensor)
            loss = criterion(output, target_tensor)
            loss.backward()
            optimizer.step()

            # Actualise la récompense cumulative pour le prochain mouvement
            cumulative_reward *= gamma


    def _simulate_move(self, board, player):
        """
        Simule un coup pour le joueur donné.
        """
        available_columns = [i for i in range(len(board[0])) if board[0][i] == 0]
        if not available_columns:
            return None
        return np.random.choice(available_columns)

    def _get_row(self, board, column):
        """
        Retourne la première ligne disponible dans une colonne.
        """
        for row in range(5, -1, -1):  # De bas en haut
            if board[row][column] == 0:
                return row

    def _check_winner(self, board):
        """
        Vérifie s'il y a un gagnant dans le plateau de Puissance 4.
        Vérifie les alignements horizontaux, verticaux et diagonaux.
        Retourne le numéro du joueur gagnant (1 ou 2) ou None si pas de gagnant.
        """
        rows = len(board)
        cols = len(board[0])

        # Vérifie les alignements horizontaux
        for row in range(rows):
            for col in range(cols - 3):  # Minimum 4 colonnes nécessaires pour un alignement
                if (
                    board[row][col] == board[row][col + 1] == board[row][col + 2] == board[row][col + 3]
                    and board[row][col] != 0
                ):
                    return board[row][col]

        # Vérifie les alignements verticaux
        for col in range(cols):
            for row in range(rows - 3):  # Minimum 4 lignes nécessaires pour un alignement
                if (
                    board[row][col] == board[row + 1][col] == board[row + 2][col] == board[row + 3][col]
                    and board[row][col] != 0
                ):
                    return board[row][col]

        # Vérifie les alignements diagonaux (montants)
        for row in range(rows - 3):
            for col in range(cols - 3):  # Vérifie si une diagonale montante est possible
                if (
                    board[row][col] == board[row + 1][col + 1] == board[row + 2][col + 2] == board[row + 3][col + 3]
                    and board[row][col] != 0
                ):
                    return board[row][col]

        # Vérifie les alignements diagonaux (descendants)
        for row in range(3, rows):
            for col in range(cols - 3):  # Vérifie si une diagonale descendante est possible
                if (
                    board[row][col] == board[row - 1][col + 1] == board[row - 2][col + 2] == board[row - 3][col + 3]
                    and board[row][col] != 0
                ):
                    return board[row][col]

        # Aucun gagnant trouvé
        return None

    def _backpropagate(self, moves, winner, optimizer, criterion):
        """
        Récompense ou pénalise les coups joués après une partie.
        """
        reward = 1 if winner == 1 else -1 if winner == 2 else 0
        for board, move, player in moves:
            target = np.zeros(7)
            target[move] = reward if player == winner else -reward
            board_tensor = torch.tensor(board, dtype=torch.float32).unsqueeze(0)
            target_tensor = torch.tensor(target, dtype=torch.float32).unsqueeze(0)

            optimizer.zero_grad()
            output = self.ai(board_tensor)
            loss = criterion(output, target_tensor)
            loss.backward()
            optimizer.step()
