import pygame
import random
from enum import Enum
from collections import namedtuple

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

Point = namedtuple("Point", "x, y")

pygame.display.init()
pygame.font.init()

font = pygame.font.Font(pygame.font.get_default_font(), 25)

# rgb colors
WHITE = (255, 255, 255)
RED = (200, 0, 0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
GREEN1 = (0, 255, 0)
GREEN2 = (0, 150, 0)
BLACK = (0, 0, 0)

BLOCK_SIZE = 20
SPEED = 4

class SnakeGame:

    def __init__(self, width=640, height=480):
        self.w = width
        self.h = height

        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption("Two Player Snake Game")
        self.clock = pygame.time.Clock()

        # Player 1 initialization
        self.direction1 = Direction.RIGHT
        self.head1 = Point(self.w / 4, self.h / 2)
        self.snake1 = [self.head1,
                      Point(self.head1.x - BLOCK_SIZE, self.head1.y),
                      Point(self.head1.x - (2 * BLOCK_SIZE), self.head1.y)]

        # Player 2 initialization
        self.direction2 = Direction.LEFT
        self.head2 = Point(3 * self.w / 4, self.h / 2)
        self.snake2 = [self.head2,
                      Point(self.head2.x + BLOCK_SIZE, self.head2.y),
                      Point(self.head2.x + (2 * BLOCK_SIZE), self.head2.y)]

        self.score1 = 0
        self.score2 = 0
        self.food = None

        self.placeFood()

    def placeFood(self):
        x = random.randint(0, (self.w - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        y = random.randint(0, (self.h - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        self.food = Point(x, y)
        if self.food in self.snake1 or self.food in self.snake2:
            self.placeFood()

    def playStep(self):
        for event in pygame.event.get():
            if event == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                # Player 1 controls
                if event.key == pygame.K_LEFT and self.direction1 != Direction.RIGHT:
                    self.direction1 = Direction.LEFT
                elif event.key == pygame.K_RIGHT and self.direction1 != Direction.LEFT:
                    self.direction1 = Direction.RIGHT
                elif event.key == pygame.K_UP and self.direction1 != Direction.DOWN:
                    self.direction1 = Direction.UP
                elif event.key == pygame.K_DOWN and self.direction1 != Direction.UP:
                    self.direction1 = Direction.DOWN

                # Player 2 controls
                if event.key == pygame.K_a and self.direction2 != Direction.RIGHT:
                    self.direction2 = Direction.LEFT
                elif event.key == pygame.K_d and self.direction2 != Direction.LEFT:
                    self.direction2 = Direction.RIGHT
                elif event.key == pygame.K_w and self.direction2 != Direction.DOWN:
                    self.direction2 = Direction.UP
                elif event.key == pygame.K_s and self.direction2 != Direction.UP:
                    self.direction2 = Direction.DOWN

        # Move the snakes
        self.moveSnake(self.snake1, self.direction1)
        self.moveSnake(self.snake2, self.direction2)

        # Check for collisions
        if self.isCollision(self.snake1): # or self.isCollision(self.snake2):
            return True, self.score1#, self.score2

        # Handle collisions between players
        if self.handlePlayerCollision():
            return True, self.score1, self.score2

        # Check if food is eaten
        if self.head1 == self.food:
            self.score1 += 1
            self.placeFood()
        else:
            self.snake1.pop()

        if self.head2 == self.food:
            self.score2 += 1
            self.placeFood()
        else:
            self.snake2.pop()

        self.updateUi()
        self.clock.tick(SPEED)
        return False, self.score1, self.score2

    def isCollision(self, snake):
        head = snake[0]

        # Check if snake hits the wall
        if head.x > self.w - BLOCK_SIZE or head.x < 0 or head.y > self.h - BLOCK_SIZE or head.y < 0:
            return True

        # Check if snake hits itself
        if head in snake[1:]:
            return True

        return False

    def handlePlayerCollision(self):
        if self.head1 in self.snake2[1:]:
            self.snake2.pop()
            if len(self.snake2) == 0:
                return True
        if self.head2 in self.snake1[1:]:
            self.snake1.pop()
            if len(self.snake1) == 0:
                return True
        if self.head1 == self.head2:
            return True
        return False

    def moveSnake(self, snake, direction):
    # Get the current head position
        head = snake[0]
        x, y = head.x, head.y

        # Update the head's position based on the direction
        if direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif direction == Direction.UP:
            y -= BLOCK_SIZE

        # Create the new head position
        new_head = Point(x, y)

        # Insert the new head at the start of the snake
        snake.insert(0, new_head)

        # Update the appropriate head attribute based on the snake
        if snake == self.snake1:
            self.head1 = new_head
        elif snake == self.snake2:
            self.head2 = new_head


    def updateUi(self):
        self.display.fill(BLACK)

        # Draw Player 1 snake
        for p in self.snake1:
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(p.x, p.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, BLUE2, pygame.Rect(p.x + 4, p.y + 4, 12, 12))

        # Draw Player 2 snake
        for p in self.snake2:
            pygame.draw.rect(self.display, GREEN1, pygame.Rect(p.x, p.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, GREEN2, pygame.Rect(p.x + 4, p.y + 4, 12, 12))

        # Draw food
        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))

        # Draw scores
        score_text = font.render(f"Player 1: {self.score1}  Player 2: {self.score2}", True, WHITE)
        self.display.blit(score_text, [0, 0])

        pygame.display.flip()
def playGame():
    game = SnakeGame()

    while True:
        game_over, score1, score2 = game.playStep()

        if game_over:
            break

    print(f"Game Over! Player 1 Score: {score1}, Player 2 Score:{score2}")
    pygame.quit()

if __name__ == "__main__":
    playGame()