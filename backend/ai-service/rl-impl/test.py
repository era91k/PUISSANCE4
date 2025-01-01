from stable_baselines3 import DQN
from connect_four_env import ConnectFourEnv
import gymnasium as gym
import os
import numpy as np

# Ensure the models directory exists
os.makedirs("models", exist_ok=True)

# Create the environment
env = ConnectFourEnv()

# Wrapper to ensure only valid actions are chosen
class ValidActionWrapper(gym.ActionWrapper):
    def __init__(self, env):
        super(ValidActionWrapper, self).__init__(env)

    def action(self, action):
        while not self.env.is_valid_action(action):
            action = self.env.action_space.sample()
        return action

# Wrap the environment
env = ValidActionWrapper(env)

# Load the trained model
model = DQN.load("models/connect_four_dqn")

# Function to print the board in a more readable format
def print_board(board):
    print("\n".join([" ".join(map(str, row)) for row in board]))
    print()

# Function to play a single game and collect experiences
def play_game():
    obs, _ = env.reset()
    done = False
    episode_experiences = []

    print("Starting game...")

    while not done:
        # Human player's turn
        print("Current board:")
        print_board(env.env.board)  # Access the underlying environment's board
        valid_move = False
        while not valid_move:
            try:
                action = int(input("Enter your move (0-6): "))
                if env.env.is_valid_action(action):  # Access the underlying environment's method
                    valid_move = True
                else:
                    print("Invalid move. Try again.")
            except ValueError:
                print("Invalid input. Enter a number between 0 and 6.")
        
        new_obs, reward, done, _, _ = env.step(action)
        episode_experiences.append((obs, action, reward, new_obs, done))
        obs = new_obs
        if done:
            if reward == 1:
                print("Human wins!")
            else:
                print("It's a draw!")
            break

        # AI's turn
        action, _ = model.predict(obs)
        while not env.env.is_valid_action(action):  # Access the underlying environment's method
            action = env.action_space.sample()
        new_obs, reward, done, _, _ = env.step(action)
        episode_experiences.append((obs, action, reward, new_obs, done))
        obs = new_obs
        print("AI played:")
        print_board(env.env.board)  # Access the underlying environment's board
        if done:
            if reward == 1:
                print("AI wins!")
            else:
                print("It's a draw!")
            break

    return episode_experiences

# Play and train the model
while True:
    experiences = play_game()
    # Add experiences to the replay buffer
    for obs, action, reward, new_obs, done in experiences:
        model.replay_buffer.add(np.array([obs]), np.array([new_obs]), np.array([action]), np.array([reward]), np.array([done]), [{}])
    # Set the environment before training
    model.set_env(env)
    # Continue training the model after each game
    model.learn(total_timesteps=1000, reset_num_timesteps=False)
    # Save the model after each training session
    model.save("models/connect_four_dqn")