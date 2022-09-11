import pygame
from constants import *
from piece import Piece

class Board:
    def __init__(self, screen, player):
        self.screen = screen
        self.player = player
        self.colors = ("w", "b")
        self.board = []
        self.create_board()

    def create_board(self):
        piece_types = ["rook", "knight", "bishop", "queen", "king", "bishop", "knight", "rook"]
        if self.player == 1:
            piece_types = list(piece_types[::-1])
        for row in range(ROWS):
            self.board.append([])
            for col in range(COLS):
                if row == 0 or row == 7:
                    self.board[row].append(Piece(row, col, piece_types[col], self.colors[0 if self.player == 1 else 1] if row <= 1 else self.colors[self.player], self.screen))
                elif row == 1 or row == 6:
                    self.board[row].append(Piece(row, col, "pawn", self.colors[0 if self.player == 1 else 1] if row <= 1 else self.colors[self.player], self.screen))
                else:
                    self.board[row].append(0)

    def get_piece(self, row, col):
        return self.board[row][col]

    def draw_board(self):
        self.draw_squares(self.screen)
        self.draw_frame(self.screen)
        self.draw_indexes(self.screen)
        self.draw_pieces(self.screen)

    def draw_pieces(self, screen):
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece != 0:
                    piece.draw_piece(screen)

    def draw_squares(self, screen):
        pygame.draw.rect(screen, BROWN, (INDEX_PADDING, INDEX_PADDING, ROWS * SQUARE_SIZE, COLS * SQUARE_SIZE))
        for row in range(ROWS):
            for col in range(row % 2, COLS, 2):
                pygame.draw.rect(screen, YELLOW, (row * SQUARE_SIZE + INDEX_PADDING, col * SQUARE_SIZE + INDEX_PADDING, SQUARE_SIZE, SQUARE_SIZE))

    def draw_frame(self, screen):
        starting_positions = [(INDEX_PADDING, INDEX_PADDING), (WIDTH - INDEX_PADDING, INDEX_PADDING), (WIDTH - INDEX_PADDING, HEIGHT - INDEX_PADDING), (INDEX_PADDING, HEIGHT - INDEX_PADDING)]
        ending_positions = [(WIDTH - INDEX_PADDING, INDEX_PADDING), (WIDTH - INDEX_PADDING, HEIGHT - INDEX_PADDING), (INDEX_PADDING, HEIGHT - INDEX_PADDING), (INDEX_PADDING, INDEX_PADDING)]
        for i in range(4):
            pygame.draw.line(screen, BLACK, starting_positions[i], ending_positions[i])

    def draw_indexes(self, screen):
        for i in range(2):
            for row in range(ROWS):
                font_obj = pygame.font.SysFont("arial black", 40)
                if self.player == 0:
                    index = str(ROWS - row)
                else:
                    index = str(row + 1)
                font = font_obj.render(index, True, BLACK)
                if i == 0:
                    screen.blit(font, (INDEX_PADDING / 3, INDEX_PADDING + 20 + row * SQUARE_SIZE))
                else:
                    screen.blit(font, (WIDTH - INDEX_PADDING * 0.6, INDEX_PADDING + 20 + row * SQUARE_SIZE))

        for j in range(2):
            for col in range(COLS):
                font_obj = pygame.font.SysFont("arial black", 40)
                if self.player == 0:
                    index2 = chr(65 + col)
                else:
                    index2 = chr(72 - col)
                font = font_obj.render(index2, True, BLACK)
                if j == 0:
                    screen.blit(font, (1.35 * INDEX_PADDING + col * SQUARE_SIZE, INDEX_PADDING * 0.2))
                else:
                    screen.blit(font, (1.35 * INDEX_PADDING + col * SQUARE_SIZE, HEIGHT - INDEX_PADDING * 0.8))

    def move(self, piece, row, col):
        self.board[piece.row][piece.col], self.board[row][col] = self.board[row][col], self.board[piece.row][piece.col]
        piece.move(row, col)

    def get_moves(self, piece):
        moves = []

        if piece.piece_type == "pawn":
            if piece.color == "w":
                if self.player == 0:
                    moves += self.check_up(piece, 2 if piece.row == 6 else 1)
                else:
                    moves += self.check_down(piece, 2 if piece.row == 1 else 1)
            else:
                if self.player == 0:
                    moves += self.check_down(piece, 2 if piece.row == 1 else 1)
                else:
                    moves += self.check_up(piece, 2 if piece.row == 6 else 1)

            if piece.col > 0:
                if self.player == 0:
                    if piece.row < 7 if piece.color == "b" else piece.row > 0:
                        if self.get_piece(piece.row - 1 if piece.color == "w" else piece.row + 1, piece.col - 1) and \
                                self.get_piece(piece.row - 1 if piece.color == "w" else piece.row + 1, piece.col - 1).color != piece.color:
                            moves.append((piece.row - 1 if piece.color == "w" else piece.row + 1, piece.col - 1))
                else:
                    if piece.row < 7 if piece.color == "w" else piece.row > 0:
                        if self.get_piece(piece.row - 1 if piece.color == "b" else piece.row + 1, piece.col - 1) and \
                                self.get_piece(piece.row - 1 if piece.color == "b" else piece.row + 1, piece.col - 1).color != piece.color:
                            moves.append((piece.row - 1 if piece.color == "b" else piece.row + 1, piece.col - 1))
            if piece.col < 7:
                if self.player == 0:
                    if piece.row < 7 if piece.color == "b" else piece.row > 0:
                        if self.get_piece(piece.row - 1 if piece.color == "w" else piece.row + 1, piece.col + 1) and \
                                self.get_piece(piece.row - 1 if piece.color == "w" else piece.row + 1, piece.col + 1).color != piece.color:
                            moves.append((piece.row - 1 if piece.color == "w" else piece.row + 1, piece.col + 1))
                else:
                    if piece.row < 7 if piece.color == "w" else piece.row > 0:
                        if self.get_piece(piece.row - 1 if piece.color == "b" else piece.row + 1, piece.col + 1) and \
                                self.get_piece(piece.row - 1 if piece.color == "b" else piece.row + 1, piece.col + 1).color != piece.color:
                            moves.append((piece.row - 1 if piece.color == "b" else piece.row + 1, piece.col + 1))

        elif piece.piece_type == "rook":
            moves += self.check_ver_hor(piece, ROWS)

        elif piece.piece_type == "bishop":
            moves += self.check_diagonals(piece, ROWS)

        elif piece.piece_type == "queen":
            moves += self.check_ver_hor(piece, ROWS)
            moves += self.check_diagonals(piece, ROWS)

        elif piece.piece_type == "king":
            moves += self.check_ver_hor(piece, 1)
            moves += self.check_diagonals(piece, 1)
            moves += self.check_for_castles(piece)

        else:
            moves += self.check_knight_moves(piece)

        return moves

    def is_check(self, turn):
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.get_piece(row, col)
                if piece:
                    if piece.color != turn:
                        moves = self.get_moves(piece)
                        for move in moves:
                            r, c = move
                            if self.get_piece(r, c):
                                if self.get_piece(r, c).piece_type == "king":
                                    return True
        return False

    def is_checkmate(self, turn):
        if self.is_check(turn):
            for row in range(ROWS):
                for col in range(COLS):
                    piece = self.get_piece(row, col)
                    if piece:
                        if piece.color == turn:
                            if self.get_valid_moves(piece, turn):
                                return False
        else:
            return False

        return True

    def is_stalemate(self, turn):
        if not self.is_check(turn):
            for row in range(ROWS):
                for col in range(COLS):
                    piece = self.get_piece(row, col)
                    if piece:
                        if piece.color == turn:
                            if self.get_valid_moves(piece, turn):
                                return False
        else:
            return False

        return True

    def get_valid_moves(self, piece, turn):
        invalid_moves = self.get_moves(piece)
        to_delete = []
        captured = False
        row, col = piece.row, piece.col
        for move in invalid_moves:
            r, c = move
            piece_ = self.get_piece(r, c)
            if piece:
                self.capture(r, c)
                captured = True
            self.move(piece, r, c)
            if self.is_check(turn):
                to_delete.append(move)
            self.move(piece, row, col)
            if captured:
                self.board[r][c] = piece_
                captured = False
            if self.is_check(turn) and piece.piece_type == "king" and move in self.check_for_castles(piece):
                to_delete.append(move)

        moves = [i for i in invalid_moves if i not in to_delete]

        return moves

    def capture(self, row, col):
        self.board[row][col] = 0

    def check_for_castles(self, piece):
        moves = []

        valid_castle = True
        corners = [(0, 0), (0, 7), (7, 0), (7, 7)]
        if piece.piece_type == "king":
            if not piece.moved:
                for i in range(2):
                    if self.player == 0:
                        pos = corners[i] if piece.color == "b" else corners[i + 2]
                    else:
                        pos = corners[i] if piece.color == "w" else corners[i + 2]

                    rook = self.get_piece(pos[0], pos[1])
                    if rook:
                        if not rook.moved:
                            col = rook.col
                            if self.player == 0:
                                _range = 3 if rook.col == 0 else 2
                            else:
                                _range = 2 if rook.col == 0 else 3
                            for _ in range(_range):
                                if rook.col == 0:
                                    col += 1
                                else:
                                    col -= 1

                                if self.get_piece(rook.row, col):
                                    valid_castle = False

                            if valid_castle:
                                moves.append((piece.row, piece.col - 2 if rook.col == 0 else piece.col + 2))
                            valid_castle = True

        return moves

    def check_knight_moves(self, piece):
        moves = []

        rows = [-2, -2, -1, 1, 2, 2, -1, 1]
        cols = [-1, 1, 2, 2, -1, 1, -2, -2]
        for i in range(8):
            if -1 < piece.row + 1 * rows[i] < 8 and -1 < piece.col + 1 * cols[i] < 8:
                if not self.get_piece(piece.row + 1 * rows[i], piece.col + 1 * cols[i]):
                    moves.append((piece.row + 1 * rows[i], piece.col + 1 * cols[i]))
                elif self.get_piece(piece.row + 1 * rows[i], piece.col + 1 * cols[i]).color != piece.color:
                    moves.append((piece.row + 1 * rows[i], piece.col + 1 * cols[i]))

        return moves

    def check_ver_hor(self, piece, rows_cols):
        moves = []

        moves += self.check_right(piece, rows_cols)
        moves += self.check_left(piece, rows_cols)
        moves += self.check_up(piece, rows_cols)
        moves += self.check_down(piece, rows_cols)

        return moves

    def check_right(self, piece, cols):
        moves = []

        for col in range(1, cols + 1):
            if -1 < piece.col + col < 8:
                if not self.get_piece(piece.row, piece.col + col):
                    moves.append((piece.row, piece.col + col))
                elif self.get_piece(piece.row, piece.col + col).color != piece.color:
                    moves.append((piece.row, piece.col + col))
                    break
                else:
                    break

        return moves

    def check_left(self, piece, cols):
        moves = []

        for col in range(1, cols + 1):
            if -1 < piece.col - col < 8:
                if not self.get_piece(piece.row, piece.col - col):
                    moves.append((piece.row, piece.col - col))
                elif self.get_piece(piece.row, piece.col - col).color != piece.color:
                    moves.append((piece.row, piece.col - col))
                    break
                else:
                    break

        return moves

    def check_up(self, piece, rows):
        moves = []

        for row in range(1, rows + 1):
            if -1 < piece.row - row < 8:
                if not self.get_piece(piece.row - row, piece.col):
                    moves.append((piece.row - row, piece.col))
                elif self.get_piece(piece.row - row, piece.col).color != piece.color:
                    if piece.piece_type != "pawn":
                        moves.append((piece.row - row, piece.col))
                    break
                else:
                    break

        return moves

    def check_down(self, piece, rows):
        moves = []

        for row in range(1, rows + 1):
            if -1 < piece.row + row < 8:
                if not self.get_piece(piece.row + row, piece.col):
                    moves.append((piece.row + row, piece.col))
                elif self.get_piece(piece.row + row, piece.col).color != piece.color:
                    if piece.piece_type != "pawn":
                        moves.append((piece.row + row, piece.col))
                    break
                else:
                    break

        return moves

    def check_diagonals(self, piece, squares):
        moves = []

        for i in range(4):
            for square in range(1, squares + 1):
                conditions = [(piece.row - square, piece.col + square), (piece.row + square, piece.col + square), (piece.row + square, piece.col - square), (piece.row - square, piece.col - square)]
                if -1 < conditions[i][0] < 8 and -1 < conditions[i][1] < 8:
                    if not self.get_piece(conditions[i][0], conditions[i][1]):
                        moves.append((conditions[i][0], conditions[i][1]))
                    elif self.get_piece(conditions[i][0], conditions[i][1]).color != piece.color:
                        moves.append((conditions[i][0], conditions[i][1]))
                        break
                    else:
                        break

        return moves