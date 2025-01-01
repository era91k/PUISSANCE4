from stable_baselines3 import DQN
from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.callbacks import BaseCallback, EvalCallback
from stable_baselines3.common.logger import configure
from connect_four_env import ConnectFourEnv
import gymnasium as gym
import numpy as np
import os

# Ensure the models directory exists
os.makedirs("models", exist_ok=True)
os.makedirs("logs", exist_ok=True)

# Create the environment
env = ConnectFourEnv()

# Check the environment
check_env(env)

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

# Path to the saved model
model_path = "models/connect_four_dqn"

# Load the existing model if it exists, otherwise create a new model
if os.path.exists(model_path + ".zip"):
    model = DQN.load(model_path, env=env)
    print("Loaded existing model.")
else:
    model = DQN("MlpPolicy", env, verbose=1, tensorboard_log="./logs/")
    print("Created new model.")

# Custom callback for TensorBoard
class TensorboardCallback(BaseCallback):
    def __init__(self, verbose=0):
        super(TensorboardCallback, self).__init__(verbose)

    def _on_step(self) -> bool:
        # Log scalar value (here a random variable)
        value = np.random.random()
        self.logger.record('random_value', value)
        return True

# Create the evaluation environment
eval_env = ValidActionWrapper(ConnectFourEnv())

# Create the evaluation callback
eval_callback = EvalCallback(eval_env, best_model_save_path='./logs/',
                             log_path='./logs/', eval_freq=500,
                             deterministic=True, render=False)

# Configure the logger to use TensorBoard
new_logger = configure("./logs/", ["tensorboard"])
model.set_logger(new_logger)

# Training the model
model.learn(total_timesteps=1000000, callback=[TensorboardCallback(), eval_callback])  # Augmenter le nombre de pas d'entraînement

# Save the model
model.save(model_path)