import numpy as np
import gymnasium as gym
from gymnasium import spaces

# Constants for the board dimensions
ROWS = 6
COLS = 7

class ConnectFourEnv(gym.Env):
    def __init__(self):
        super(ConnectFourEnv, self).__init__()
        
        # Initialize the game board: 6 rows, 7 columns, empty cells initialized to 0
        self.board = np.zeros((ROWS, COLS), dtype=int)
        
        # Player 1 starts (1) and Player 2 (2)
        self.current_player = 1 
        
        # Action space: 7 possible actions (each column)
        self.action_space = spaces.Discrete(COLS) 
        
        # Observation space: Flattened 6x7 board with values between 0 (empty), 1 (player 1), and 2 (player 2)
        self.observation_space = spaces.Box(low=0, high=2, shape=(ROWS * COLS,), dtype=int)
    
    def reset(self, seed=None, options=None):
        """
        Resets the board to the initial state for a new game.
        """
        super().reset(seed=seed)
        self.board = np.zeros((ROWS, COLS), dtype=int)
        self.current_player = 1  # Player 1 starts
        return self.board.flatten(), {}
    
    def step(self, action):
        """
        Executes a single step in the environment based on the chosen action (column).
        """
        # Validate the action: Check if the column is within range and not full
        if not self.is_valid_action(action):
            raise ValueError(f"Invalid action: Column {action} is full or out of range.")
        
        # Drop the piece in the chosen column
        row = self.get_next_open_row(action)
        self.board[row][action] = self.current_player
        
        # Check if the current player wins
        reward = 1 if self.check_winner(self.current_player) else 0
        if reward == 0 and self.check_winner(3 - self.current_player):
            reward = -1  # Penalize if the opponent is about to win
        terminated = reward == 1 or self.is_draw()
        
        # Switch player
        self.current_player = 3 - self.current_player  # Toggle between player 1 and 2
        
        return self.board.flatten(), reward, bool(terminated), False, {}
    
    def is_valid_action(self, action):
        """
        Check if a column is valid for a move (within range and not full).
        """
        if action < 0 or action >= COLS:
            return False  # Out of bounds
        return self.board[0][action] == 0  # Column is not full
    
    def get_next_open_row(self, action):
        """
        Find the next available row in the chosen column to drop the piece.
        """
        for r in range(ROWS-1, -1, -1):
            if self.board[r][action] == 0:
                return r
        return -1  # This should never be hit due to the validity check
    
    def check_winner(self, player):
        """
        Check if the current player has won (horizontal, vertical, diagonal).
        """
        # Horizontal check
        for c in range(COLS - 3):
            for r in range(ROWS):
                if all(self.board[r, c+i] == player for i in range(4)):
                    return True
        
        # Vertical check
        for c in range(COLS):
            for r in range(ROWS - 3):
                if all(self.board[r+i, c] == player for i in range(4)):
                    return True
        
        # Diagonal check (positive slope)
        for c in range(COLS - 3):
            for r in range(ROWS - 3):
                if all(self.board[r+i, c+i] == player for i in range(4)):
                    return True
        
        # Diagonal check (negative slope)
        for c in range(COLS - 3):
            for r in range(3, ROWS):
                if all(self.board[r-i, c+i] == player for i in range(4)):
                    return True
        
        return False
    
    def is_draw(self):
        """
        Check if the game is a draw (no empty spaces remaining).
        """
        return np.all(self.board != 0)

# If you'd like to test the environment
if __name__ == "__main__":
    env = ConnectFourEnv()
    print("Initial Board:")
    print(env.reset())  # Print the initial empty board
    
    # Example of taking a step
    try:
        action = 3  # Player chooses to drop a piece in column 3
        obs, reward, terminated, truncated, info = env.step(action)
        print("Board after action:")
        print(obs)
        print(f"Reward: {reward}, Terminated: {terminated}")
    except ValueError as e:
        print(f"Error: {e}")