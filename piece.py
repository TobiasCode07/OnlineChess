import pygame
from constants import *

class Piece:
    def __init__(self, row, col, piece_type, color, screen):
        self.row = row
        self.col = col
        self.piece_type = piece_type
        self.color = color
        self.screen = screen
        self.moved = False

    def draw_piece(self, screen):
        piece_img = pygame.image.load(PIECE_PATH.replace("x", f"{self.color}_{self.piece_type}"))
        screen.blit(piece_img, (SQUARE_SIZE * (self.col + 1) + 10, SQUARE_SIZE * (self.row + 1) + 10))

    def move(self, row, col):
        self.row = row
        self.col = col