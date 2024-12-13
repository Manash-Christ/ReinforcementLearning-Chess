from collections import deque
import random

import numpy as np
import torch

from models import LinearQNet, QTrainer
from environ import Point, BLOCK_SIZE, Direction




MAX_MEMORY = 100_000
BATCH_SIZE = 256
LR = 0.001

class Agent:
    def __init__(self, player_id):
        self.numberOfGames = 0
        self.player_id = player_id
        self.epsilon = 1
        self.gamma = 0.90
        self.memory = deque(maxlen=MAX_MEMORY)
        self.model = LinearQNet(11, 512, 256, 3)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

    def getState(self, game):
        if self.player_id == 1:
            head = game.head1
            direction = game.direction1
        else:
            head = game.head2
            direction = game.direction2

        point_left = Point(head.x - BLOCK_SIZE, head.y)
        point_right = Point(head.x + BLOCK_SIZE, head.y)
        point_up = Point(head.x, head.y - BLOCK_SIZE)
        point_down = Point(head.x, head.y + BLOCK_SIZE)

        direction_left = direction == Direction.LEFT
        direction_right = direction == Direction.RIGHT
        direction_up = direction == Direction.UP
        direction_down = direction == Direction.DOWN


        nearest_fruit = min(game.food, key=lambda fruit: abs(fruit.x - head.x) + abs(fruit.y - head.y))

        state = [
            (direction_right and game.isCollision(point_right)) or
            (direction_left and game.isCollision(point_left)) or
            (direction_up and game.isCollision(point_up)) or
            (direction_down and game.isCollision(point_down)),
    
            (direction_up and game.isCollision(point_right)) or
            (direction_down and game.isCollision(point_left)) or
            (direction_left and game.isCollision(point_up)) or
            (direction_right and game.isCollision(point_down)),
    
            (direction_down and game.isCollision(point_right)) or
            (direction_up and game.isCollision(point_left)) or
            (direction_right and game.isCollision(point_up)) or
            (direction_left and game.isCollision(point_down)),
    
            direction_left,
            direction_right,
            direction_up,
            direction_down,
    
            nearest_fruit.x < head.x, 
            nearest_fruit.x > head.x, 
            nearest_fruit.y < head.y, 
            nearest_fruit.y > head.y  
        ]

        return np.array(state, dtype=int)

    def remember(self, state, action, reward, nextState, done):
        self.memory.append((state, action, reward, nextState, done))

    def trainLongMemory(self):
        if len(self.memory) < BATCH_SIZE:
            sample = self.memory
        else:
            sample = random.sample(self.memory, BATCH_SIZE)

        states, actions, rewards, nextStates, dones = zip(*sample)
        self.trainer.trainStep(states, actions, rewards, nextStates, dones)

    def trainShortMemory(self, state, action, reward, nextState, done):
        self.trainer.trainStep(state, action, reward, nextState, done)

    def getAction(self, state):

        self.epsilon = max(0.01, self.epsilon * 0.995)  # Ensure epsilon doesn't fall below 0.01

        # self.epsilon = 80 - self.numberOfGames
        finalMove = [0, 0, 0]

        # if random.randint(0, 200) < self.epsilon:
        if random.uniform(0, 1) < self.epsilon:
            move = random.randint(0, 2)
            finalMove[move] = 1
        else:
            stateTensor = torch.tensor(state, dtype=torch.float)
            prediction = self.model(stateTensor)
            move = torch.argmax(prediction).item()
            finalMove[move] = 1

        return finalMove
