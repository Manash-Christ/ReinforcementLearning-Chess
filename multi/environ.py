import numpy as np
import pygame
import random
from enum import Enum
from collections import namedtuple
from math import sqrt


class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

Point = namedtuple("Point", "x, y")

pygame.display.init()
pygame.font.init()

font = pygame.font.Font(pygame.font.get_default_font(), 25)

WHITE = (255, 255, 255)
RED = (200, 0, 0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
GREEN1 = (0, 255, 0)
GREEN2 = (0, 150, 0)
BLACK = (0, 0, 0)

BLOCK_SIZE = 20
SPEED = 240


def calculateDistance(point1, point2):
    return sqrt((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2)

def getClosestFood(head, foodList):
    return min(foodList, key=lambda food: calculateDistance(head, food))



class MultiplayerSnakeGameAI:

    def __init__(self, width=640, height=480):
        self.w = width
        self.h = height

        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption("Multiplayer Snake AI Game")
        self.clock = pygame.time.Clock()

        self.direction1 = Direction.RIGHT
        self.head1 = Point(self.w / 4, self.h / 2)
        self.snake1 = [self.head1,
                    Point(self.head1.x - BLOCK_SIZE, self.head1.y),
                      Point(self.head1.x - (2 * BLOCK_SIZE), self.head1.y)]

        self.direction2 = Direction.LEFT
        self.head2 = Point(3 * self.w / 4, self.h / 2)
        self.snake2 = [self.head2,
                    Point(self.head2.x + BLOCK_SIZE, self.head2.y),
                      Point(self.head2.x + (2 * BLOCK_SIZE), self.head2.y)]

        self.score1 = 0
        self.score2 = 0
    
        self.food = []
        self.placeFood(initial=True) # <- fix 5


        self.frameIteration = 0

    def reset(self):
        print('--RESET--')
        self.direction1 = Direction.RIGHT
        self.head1 = Point(self.w / 4, self.h / 2)
        self.snake1 = [self.head1,
                    Point(self.head1.x - BLOCK_SIZE, self.head1.y),
                      Point(self.head1.x - (4 * BLOCK_SIZE), self.head1.y)]

        self.direction2 = Direction.LEFT
        self.head2 = Point(3 * self.w / 4, self.h / 2)
        self.snake2 = [self.head2,
                    Point(self.head2.x + BLOCK_SIZE, self.head2.y),
                      Point(self.head2.x + (4 * BLOCK_SIZE), self.head2.y)]
        
        # print(f"Debug: Reset Player 1 head: {self.head1}, Player 2 head: {self.head2}")


        self.score1 = 0
        self.score2 = 0
        self.food = []
        self.placeFood(initial=True)
        self.frameIteration = 0



    def placeFood(self, initial=False):
        num_fruits = 10 if initial else 1
        for _ in range(num_fruits):
            while True:
                x = random.randint(0, (self.w - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
                y = random.randint(0, (self.h - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
                new_fruit = Point(x, y)
    
                if new_fruit not in self.snake1 and new_fruit not in self.snake2 and new_fruit not in self.food:
                    self.food.append(new_fruit)
                    break

    def playStep(self, action1, action2):

        closest_food1 = getClosestFood(self.head1, self.food)
        closest_food2 = getClosestFood(self.head2, self.food)
        distance_before1 = calculateDistance(self.head1, closest_food1)
        distance_before2 = calculateDistance(self.head2, closest_food2)
        # print(f"Debug: Before Step - Player 1 head: {self.head1}, Player 2 head: {self.head2}")

        self.frameIteration += 1

        self.moveSnake(self.snake1, self.direction1, action1)
        self.moveSnake(self.snake2, self.direction2, action2)

        closest_food1 = getClosestFood(self.head1, self.food)
        closest_food2 = getClosestFood(self.head2, self.food)
        distance_after1 = calculateDistance(self.head1, closest_food1)
        distance_after2 = calculateDistance(self.head2, closest_food2)
    
        proximity_reward1 = 7 if distance_after1 < distance_before1 else -7
        proximity_reward2 = 3 if distance_after2 < distance_before2 else -3

        

        if self.isCollision(self.head1) or self.isCollision(self.head2):
            if self.isCollision(self.head1):
                return (-10 + proximity_reward1, 15), True, self.score1, self.score2
            elif self.isCollision(self.head2):
                return (15, -10 + proximity_reward2), True, self.score1, self.score2
            else:
                pass

        if self.handlePlayerCollision():
            if len(self.snake1) == 0 or len(self.snake2) == 0:
                return (-10, -10), True, self.score1, self.score2
    
            if self.head1 == self.head2:
                return (-10 + proximity_reward1, -10 + proximity_reward2), True, self.score1, self.score2
    
            return (-5 + proximity_reward1, -5 + proximity_reward2), False, self.score1, self.score2


        

        reward1 = 0
        reward2 = 0

        for fruit in self.food[:]:  
            if self.head1 == fruit:
                self.food.remove(fruit)
                self.score1 += 1
                reward1 = 50
                self.placeFood() 
            if self.head2 == fruit:
                self.food.remove(fruit)
                self.score2 += 1
                reward2 = 50
                self.placeFood() 

        if self.head1 not in self.food:
            self.snake1.pop()
        if self.head2 not in self.food:
            self.snake2.pop()
    
            self.updateUi()
            self.clock.tick(SPEED)

        return (reward1, reward2), False, self.score1, self.score2

    # def isCollision(self, snake):
    #     head = snake[0]

    #     if head.x > self.w - BLOCK_SIZE or head.x < 0 or head.y > self.h - BLOCK_SIZE or head.y < 0:
    #         return True

    #     if head in snake[1:]:
    #         return True

    #     return False

    def isCollision(self, p: Point = None):  # <- fix 2
        if p is None:
            raise ValueError("Point parameter 'p' must not be None.")

        if p == self.head1:
        
            if p.x >= self.w or p.x < 0 or p.y >= self.h or p.y < 0:
                print('Blue hit the boundary')
                return True
    
            if p in self.snake1[1:]:
                print('Blue killed itself')
                return True

        elif p == self.head2:
            if p.x >= self.w or p.x < 0 or p.y >= self.h or p.y < 0:
                print('Green hit the boundary')
                return True
        
            if p in self.snake2[1:]:
                print('Green killed itself')
                return True
    
        return False


    # def handlePlayerCollision(self):
    #     if self.head1 in self.snake2[1:]:
    #         self.snake2.pop()
    #         # if len(self.snake2) == 0:
    #         #     return True
    #     if self.head2 in self.snake1[1:]:
    #         self.snake1.pop()
    #         # if len(self.snake1) == 0:
    #         #     return True
    #     if self.head1 == self.head2:
    #         return True
    #     return False

    def handlePlayerCollision(self):
        collision_occurred = False
    
        if self.head1 in self.snake2[1:]:
            print(f"Blue's head collided with Green's body at {self.head1} with Green's length {len(self.snake2)}")
            self.snake2.pop()
            collision_occurred = True
            print(f"Green's snake length after collision: {len(self.snake2)}")
            if len(self.snake2) == 0:
                print("Green's snake is completely destroyed!")
                return True
    
        if self.head2 in self.snake1[1:]:
            print(f"Green's head collided with Blue's body at {self.head2} with Blue's length {len(self.snake1)}")
            self.snake1.pop()
            collision_occurred = True
            print(f"Blue's snake length after collision: {len(self.snake1)}")
            if len(self.snake1) == 0:
                print("Blue's snake is completely destroyed!")
                return True
    
        if self.head1 == self.head2:
            print("Players collided head-to-head!")
            return True
    
        return collision_occurred



    def moveSnake(self, snake, direction, action=None):

        # if snake == self.snake1:
        #     print(f"Debug: Player 1 moved to new head: {self.head1}")
        # elif snake == self.snake2:
        #     print(f"Debug: Player 2 moved to new head: {self.head2}")
        if action is not None:  # AI-controlled
            clockWiseDirections = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
            currentDirectionIndex = clockWiseDirections.index(direction)

            if np.array_equal(action, [0, 1, 0]):
                direction = clockWiseDirections[(currentDirectionIndex + 1) % 4]
            elif np.array_equal(action, [0, 0, 1]):
                direction = clockWiseDirections[(currentDirectionIndex - 1) % 4]

            if snake == self.snake1:
                self.direction1 = direction
            elif snake == self.snake2:
                self.direction2 = direction

        head = snake[0]
        x, y = head.x, head.y

        if direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif direction == Direction.UP:
            y -= BLOCK_SIZE

        new_head = Point(x, y)
        snake.insert(0, new_head)

        if snake == self.snake1:
            self.head1 = new_head
        elif snake == self.snake2:
            self.head2 = new_head

    def updateUi(self):
        self.display.fill(BLACK)

        for p in self.snake1:
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(p.x, p.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, BLUE2, pygame.Rect(p.x + 4, p.y + 4, 12, 12))

        for p in self.snake2:
            pygame.draw.rect(self.display, GREEN1, pygame.Rect(p.x, p.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, GREEN2, pygame.Rect(p.x + 4, p.y + 4, 12, 12))

        for fruit in self.food:
            pygame.draw.rect(self.display, RED, pygame.Rect(fruit.x, fruit.y, BLOCK_SIZE, BLOCK_SIZE))
            
        score_text = font.render(f"BLUE: {self.score1}  GREEN: {self.score2}", True, WHITE)
        self.display.blit(score_text, [0, 0])

        pygame.display.flip()
