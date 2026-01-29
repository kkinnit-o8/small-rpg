import pygame

# Initialize Pygame
pygame.init()

#window
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2p Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


class Player:
    def __init__(self, x, y, color, controls):
        self.x = x
        self.y = y
        self.color = color
        self.controls = controls