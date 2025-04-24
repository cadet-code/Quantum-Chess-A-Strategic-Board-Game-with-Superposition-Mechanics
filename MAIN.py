import pygame
import numpy as np
import sys
from math import inf
from random import choices

# Constants
BOARD_SIZE = 10
SQUARE_SIZE = 60
WIDTH, HEIGHT = BOARD_SIZE * SQUARE_SIZE, BOARD_SIZE * SQUARE_SIZE
COLORS = {
    'white': (255, 255, 255),
    'black': (0, 0, 0),
    'grey': (128, 128, 128),
    'blue': (0, 0, 255),
    'quantum': (0, 255, 255)
}

# Piece types and values
PIECES = {
    'P': {'value': 1, 'symbol': '♟'},
    'R': {'value': 5, 'symbol': '♜'},
    'N': {'value': 3, 'symbol': '♞'},
    'B': {'value': 3, 'symbol': '♝'},
    'Q': {'value': 9, 'symbol': '♛'},
    'K': {'value': 100, 'symbol': '♚'},
    'QN': {'value': 4, 'symbol': '♘'},  # Quantum Knight
    'EN': {'value': 6, 'symbol': '♖'}   # Entangler
}

class Piece:
    def __init__(self, color, piece_type, position):
        self.color = color
        self.type = piece_type
        self.quantum_states = [{'position': position, 'probability': 1.0}]
        self.entangled_with = None

    def collapse_state(self):
        if len(self.quantum_states) > 1:
            positions = [s['position'] for s in self.quantum_states]
            probabilities = [s['probability'] for s in self.quantum_states]
            chosen_idx = choices(range(len(positions)), weights=probabilities)[0]
            self.quantum_states = [self.quantum_states[chosen_idx]]

    def get_position(self):
        return max(self.quantum_states, key=lambda x: x['probability'])['position']

class QuantumChessGame:
    def __init__(self):
        self.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.current_player = 'white'
        self.pieces = []
        self.initialize_board()

    def initialize_board(self):
        for color in ['white', 'black']:
            row = 0 if color == 'black' else BOARD_SIZE - 1
            self.pieces.append(Piece(color, 'QN', (1, row)))
            self.pieces.append(Piece(color, 'EN', (BOARD_SIZE - 2, row)))

    def get_possible_moves(self, piece):
        moves = []
        x, y = piece.get_position()
        if piece.type == 'QN':
            patterns = [(2, 1), (1, 2), (-1, 2), (-2, 1)]
            for dx, dy in patterns:
                moves.append((x + dx, y + dy))
        elif piece.type == 'EN':
            for i in range(-3, 4):
                moves.append((x + i, y))
                moves.append((x, y + i))
        return [(nx, ny) for nx, ny in moves if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE]

    def make_move(self, piece, new_position, is_quantum=False):
        if is_quantum:
            for state in piece.quantum_states:
                state['probability'] *= 0.5
            piece.quantum_states.append({'position': new_position, 'probability': 0.5})
        else:
            piece.collapse_state()
            piece.quantum_states[0]['position'] = new_position
        self.current_player = 'black' if self.current_player == 'white' else 'white'

class GUI:
    def __init__(self, game):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.game = game
        self.selected_piece = None

    def draw_board(self):
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                color = COLORS['white'] if (x + y) % 2 == 0 else COLORS['grey']
                pygame.draw.rect(self.screen, color, (x * SQUARE_SIZE, y * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def draw_pieces(self):
        for piece in self.game.pieces:
            for state in piece.quantum_states:
                x, y = state['position']
                alpha = int(255 * state['probability'])
                text = pygame.font.SysFont('arial', 32).render(
                    PIECES[piece.type]['symbol'], True, (0, 0, 0, alpha)
                )
                self.screen.blit(text, (x * SQUARE_SIZE + 15, y * SQUARE_SIZE + 10))

    def handle_click(self, pos):
        x, y = pos[0] // SQUARE_SIZE, pos[1] // SQUARE_SIZE
        if self.selected_piece:
            self.game.make_move(self.selected_piece, (x, y))
            self.selected_piece = None
        else:
            for piece in self.game.pieces:
                if any(s['position'] == (x, y) for s in piece.quantum_states) and piece.color == self.game.current_player:
                    self.selected_piece = piece
                    break

    def main_loop(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(pygame.mouse.get_pos())

            self.draw_board()
            self.draw_pieces()
            pygame.display.flip()

if __name__ == "__main__":
    game = QuantumChessGame()
    gui = GUI(game)
    gui.main_loop()
