import os
import tensorflow as tf
from tensorflow.keras import layers
import numpy as np
import random

class DQNAgent:
    def __init__(self, state_size, action_size, load=False):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = []
        self.gamma = 0.95  # Discount factor
        self.epsilon = 1  # Exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.batch_size = 64
        self.maxlen = 50000
        self.generation = 0
        self.store = None
        self.load = load
        self.model = self._build_model()
        self.targetModel = tf.keras.models.clone_model(self.model)
        self.targetModel.set_weights(self.model.get_weights())

    def _load_model(self):
        i = 1
        j = 0
        while os.path.isfile(f"rons/RonV{i}.keras"):
            j = i
            i += 1
        if j == 0:
            model = tf.keras.Sequential([
            layers.Dense(24, activation='relu', input_shape=(self.state_size,)),
            layers.Dense(24, activation='relu'),
            layers.Dense(self.action_size, activation='linear')
            ])
            
            return model
        else:
            print(f"Loading rons/RonV{j}.keras")
            return tf.keras.models.load_model(f"rons/RonV{j}.keras", compile=False)

    def _build_model(self):
        if self.load:
            model = self._load_model()
        else:
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
        print(q_values)
        return np.argmax(q_values[0])

    # def train(self):
    #     if len(self.memory) < self.batch_size:
    #         return  # If there aren't enough experiences in memory, do nothing.

    #     self.generation += 1
    #     # Sample a batch of experiences
    #     batch = random.sample(self.memory, self.batch_size)

    #     for state, action, reward, next_state, done in batch:
    #         target = reward
    #         if not done:
    #             # Predict the Q-values for the next state
    #             next_state = np.reshape(next_state, [1, self.state_size])  # Ensure the shape is (1, state_size)
    #             target = reward + self.gamma * np.max(self.model.predict(next_state)[0])

    #         # Predict the Q-values for the current state
    #         state = np.reshape(state, [1, self.state_size])  # Ensure the shape is (1, state_size)
    #         q_values = self.model.predict(state)

    #         # Update the Q-value for the selected action
    #         q_values[0][action] = target

    #         # Train the model on the updated Q-values
    #         self.model.fit(state, q_values, epochs=1, verbose=0)

    #     # Clear memory to avoid excessive usage
    #     while len(self.memory) > self.maxlen:
    #         self.memory.pop(0)
    #     # Decay epsilon to reduce exploration over time
    #     if self.epsilon > self.epsilon_min:
    #         self.epsilon = max(self.epsilon * self.epsilon_decay, self.epsilon_min)


    def train(self):
        if len(self.memory) < self.batch_size:
            return  # If there aren't enough experiences in memory, do nothing.

        self.generation += 1
        # Sample a batch of experiences
        batch = random.sample(self.memory, self.batch_size)

        # Extract states, next_states, actions, and rewards from the batch
        states = np.array([experience[0].flatten() for experience in batch])  # Current states
        actions = np.array([experience[1] for experience in batch])  # Actions taken
        rewards = np.array([experience[2] for experience in batch])  # Rewards received
        next_states = np.array([experience[3].flatten() for experience in batch])  # Next states
        dones = np.array([experience[4] for experience in batch])  # Done flags

        # Predict Q-values for current states and next states in a single batch call
        q_values = self.targetModel.predict(states)
        q_values_next = self.targetModel.predict(next_states)

        # Update Q-values for each experience in the batch
        for i in range(len(batch)):
            target = rewards[i]
            if not dones[i]:
                target += self.gamma * np.max(q_values_next[i])  # Bellman equation update

            # Update the Q-value for the selected action
            q_values[i][actions[i]] = target

        # Train the model on the entire batch in one step
        self.model.fit(states, q_values, epochs=1, verbose=0)


        # Clear memory to avoid excessive usage
        while len(self.memory) > self.maxlen:
            self.memory.pop(0)

        if self.generation % 10 == 0:
            print("Updating Target Network")
            self.update_target_network()

        # Decay epsilon to reduce exploration over time
        if self.epsilon > self.epsilon_min:
            self.epsilon = max(self.epsilon * self.epsilon_decay, self.epsilon_min)

    def update_target_network(self):
        self.targetModel.set_weights(self.model.get_weights())
