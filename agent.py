import tensorflow as tf
from tensorflow.keras import layers
import numpy as np
import random

class DQNAgent:
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = []
        self.gamma = 0.95  # Discount factor
        self.epsilon = 1  # Exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.batch_size = 32
        self.model = self._build_model()

    def _build_model(self):
        model = tf.keras.Sequential([
            layers.Dense(24, activation='relu', input_shape=(self.state_size,)),
            layers.Dense(24, activation='relu'),
            layers.Dense(self.action_size, activation='linear')
        ])
        model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=self.learning_rate),
                      loss='mse')
        return model

    def remember(self, state, action, reward, next_state, done):
        """Store experience in replay memory."""
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state):
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        q_values = self.model.predict(state)
        return np.argmax(q_values[0])

    # def train(self):
    #     """Train the model using experience replay."""
    #     for state, action, reward, next_state, done in self.memory:
    #         target = reward
    #         if not done:
    #             target = reward + self.gamma * np.max(self.model.predict(next_state)[0])

    #         q_values = self.model.predict(state)
    #         q_values[0][action] = target  # Update Q-value for the selected action
    #         q_values = self.model.predict(np.reshape(state, [1, self.state_size]))  # Predict on reshaped state
    #         print(f"Q-values: {q_values[0]}")

    #         self.model.fit(state, q_values, epochs=1, verbose=0)  # Train the model
    #     self.memory = []
    #     if self.epsilon > self.epsilon_min:
    #         self.epsilon *= self.epsilon_decay  # Reduce exploration over time

    def train(self):
        if len(self.memory) < self.batch_size:
            return  # If there aren't enough experiences in memory, do nothing.

        # Sample a batch of experiences
        batch = random.sample(self.memory, self.batch_size)

        for state, action, reward, next_state, done in batch:
            target = reward
            if not done:
                # Predict the Q-values for the next state
                next_state = np.reshape(next_state, [1, self.state_size])  # Ensure the shape is (1, state_size)
                target = reward + self.gamma * np.max(self.model.predict(next_state)[0])

            # Predict the Q-values for the current state
            state = np.reshape(state, [1, self.state_size])  # Ensure the shape is (1, state_size)
            q_values = self.model.predict(state)

            # Update the Q-value for the selected action
            q_values[0][action] = target

            # Train the model on the updated Q-values
            self.model.fit(state, q_values, epochs=1, verbose=0)

        # Clear memory to avoid excessive usage
        self.memory = []

        # Decay epsilon to reduce exploration over time
        if self.epsilon > self.epsilon_min:
            self.epsilon = max(self.epsilon * self.epsilon_decay, self.epsilon_min)
