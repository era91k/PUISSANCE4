class Game:
    def __init__(self):
        # Crée un plateau vide (6 lignes, 7 colonnes)
        self.board = [[0] * 7 for _ in range(6)]
        self.current_turn = 1  # Le joueur 1 commence
        self.game_over = False

    def display_board(self):
        # Affiche le plateau de jeu
        for row in self.board:
            print(" | ".join(str(cell) if cell != 0 else "." for cell in row))
        print("-" * 29)

    def place_piece(self, column, player):
        # Insère une pièce dans la colonne spécifiée
        for row in reversed(self.board):
            if row[column] == 0:
                row[column] = player
                return True
        return False

    def is_over(self):
        # Simple vérification si la partie est terminée (exemple basique)
        return self.game_over or self.check_winner() or self.is_draw()

    def check_winner(self):
    # Vérifie chaque cellule du plateau pour trouver un alignement gagnant
        for row in range(6):        
            for col in range(7):
                player = self.board[row][col]
                if player == 0:
                    continue  # Ignore les cellules vides

                # Vérifier l'alignement horizontal
                if col <= 3 and all(self.board[row][col + i] == player for i in range(4)):
                    return True

                # Vérifier l'alignement vertical
                if row <= 2 and all(self.board[row + i][col] == player for i in range(4)):
                    return True

                # Vérifier l'alignement diagonal (de gauche à droite)
                if row <= 2 and col <= 3 and all(self.board[row + i][col + i] == player for i in range(4)):
                    return True

                # Vérifier l'alignement diagonal (de droite à gauche)
                if row <= 2 and col >= 3 and all(self.board[row + i][col - i] == player for i in range(4)):
                    return True

        return False


    def is_draw(self):
        # Vérifie si toutes les colonnes sont remplies
        return all(cell != 0 for row in self.board for cell in row)
