import pygame
from constants import *
from board import Board
from tkinter import *
from pygame import mixer
from _thread import *

mixer.init()

class Player:
    def __init__(self, screen, s, player):
        self.screen = screen
        self.s = s
        self.player = player
        self.selected = None
        self.turn = "w"
        self.turns = ("w", "b")
        self.int_turn = self.turns.index(self.turn)
        self.board = Board(self.screen, self.player)
        self.valid_moves = []
        self.select_frame = None
        self.check_frame = None
        self.over = False
        mixer.music.load(GAME_START_PATH)
        mixer.music.play()

    def _send(self, message):
        print(f"Sending: {message}")
        self.s.sendall(message)

    def update(self):
        self.board.draw_board()
        self.draw_valid_moves(self.valid_moves)
        self.draw_select_frame()
        self.draw_check_frame()

    def select(self, row, col):
        if self.selected:
            result = self._move(row, col)
            if not result:
                self.selected = None
                self.select_frame = None
                self.s.sendall("UNSELECT".encode())
                self.select(row, col)

        piece = self.board.get_piece(row, col)
        if piece != 0 and piece.color == self.turn:
            self.selected = piece
            self.select_frame = (piece.row, piece.col)
            self._send(f"Selected: {piece.row},{piece.col}".encode())
            self.valid_moves = self.board.get_valid_moves(piece, self.turn)
            return True

        self.valid_moves = []
        return False

    def draw_select_frame(self):
        if self.select_frame:
            pygame.draw.rect(self.screen, GREEN, pygame.Rect(self.select_frame[1] * SQUARE_SIZE + INDEX_PADDING, self.select_frame[0] * SQUARE_SIZE + INDEX_PADDING, SQUARE_SIZE, SQUARE_SIZE), 3)

    def draw_check_frame(self):
        if self.check_frame:
            pygame.draw.rect(self.screen, RED, pygame.Rect(self.check_frame[1] * SQUARE_SIZE + INDEX_PADDING, self.check_frame[0] * SQUARE_SIZE + INDEX_PADDING, SQUARE_SIZE, SQUARE_SIZE), 3)

    def get_king_pos(self, color):
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board.get_piece(row, col)
                if piece:
                    if piece.piece_type == "king" and piece.color == color:
                        return (piece.row, piece.col)

    def _move(self, row, col):
        castle = False
        if self.selected and (row, col) in self.valid_moves:
            r, c = self.selected.row, self.selected.col
            if self.board.get_piece(row, col):
                self.board.capture(row, col)
                self.board.move(self.selected, row, col)
                if self.board.is_checkmate("w" if self.turn == "b" else "b"):
                    self.check_frame = (self.get_king_pos("w" if self.turn == "b" else "b"))
                    mixer.music.load(CHECKMATE_PATH)
                    mixer.music.play()
                    start_new_thread(self.game_over, (self.turn, "checkmate"))

                elif self.board.is_stalemate("w" if self.turn == "b" else "b"):
                    self.check_frame = (self.get_king_pos("w" if self.turn == "b" else "b"))
                    mixer.music.load(STALEMATE_PATH)
                    mixer.music.play()
                    start_new_thread(self.game_over, (self.turn, "stalemate"))

                elif self.board.is_check("w" if self.turn == "b" else "b"):
                    self.check_frame = (self.get_king_pos("w" if self.turn == "b" else "b"))
                    mixer.music.load(CHECK_PATH)
                    mixer.music.play()

                else:
                    self.check_frame = None
                    mixer.music.load(CAPTURE_PATH)
                    mixer.music.play()

            else:
                if (row, col) in self.board.check_for_castles(self.selected):
                    castle = True

                self.board.move(self.selected, row, col)

                if self.board.is_checkmate("w" if self.turn == "b" else "b"):
                    self.check_frame = (self.get_king_pos("w" if self.turn == "b" else "b"))
                    mixer.music.load(CHECKMATE_PATH)
                    mixer.music.play()
                    start_new_thread(self.game_over, (self.turn, "checkmate"))

                elif self.board.is_stalemate("w" if self.turn == "b" else "b"):
                    self.check_frame = (self.get_king_pos("w" if self.turn == "b" else "b"))
                    mixer.music.load(STALEMATE_PATH)
                    mixer.music.play()
                    start_new_thread(self.game_over, (self.turn, "stalemate"))

                elif self.board.is_check("w" if self.turn == "b" else "b"):
                    self.check_frame = (self.get_king_pos("w" if self.turn == "b" else "b"))
                    mixer.music.load(CHECK_PATH)
                    mixer.music.play()

                elif castle:
                    if self.player == 0:
                        rook_col = col + 1 if col > 4 else col - 2
                    else:
                        rook_col = col + 2 if col > 4 else col - 1

                    rook = self.board.get_piece(row, rook_col)

                    if self.player == 0:
                        rook_move_col = rook.col - 2 if rook.col == 7 else rook.col + 3
                    else:
                        rook_move_col = rook.col - 3 if rook.col == 7 else rook.col + 2

                    self.check_frame = None
                    self.board.move(rook, rook.row, rook_move_col)
                    mixer.music.load(CASTLE_PATH)
                    mixer.music.play()

                else:
                    self.check_frame = None
                    mixer.music.load(MOVE_PATH)
                    mixer.music.play()

            piece = self.board.get_piece(row, col)
            piece.moved = True
            if piece.piece_type == "pawn" and piece.row == 0 and self.int_turn == self.player:
                self.promotion(piece, r, c, row, col)
            else:
                self.s.sendall(f"Moved: {r},{c},{row},{col}".encode())

            self.selected = None
            self.select_frame = None
            self.change_turn()
        else:
            self.selected = None
            self.select_frame = None
            self.s.sendall("UNSELECT".encode())
            return False

        return True

    def change_turn(self):
        self.valid_moves = []
        if self.turn == "w":
            self.turn = "b"
        else:
            self.turn = "w"

        self.int_turn = self.turns.index(self.turn)

    def draw_valid_moves(self, moves):
        for move in moves:
            row, col = move
            pygame.draw.circle(self.screen, LIGHT_BROWN, (INDEX_PADDING + SQUARE_SIZE * col + SQUARE_SIZE // 2, INDEX_PADDING + SQUARE_SIZE * row + SQUARE_SIZE // 2), 20)

    def game_over(self, winner, type):
        self.over = True
        self.selected = None
        self.select_frame = None

        root = Tk()
        root.title(f"Game over")
        root.iconbitmap(ICON_PATH_ICO)
        root.resizable(False, False)
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width / 2) - (GAME_OVER_WIDTH / 2)
        y = (screen_height / 2) - (GAME_OVER_HEIGHT / 2)
        root.geometry(f"{GAME_OVER_WIDTH}x{GAME_OVER_HEIGHT}+{int(x)}+{int(y)}")

        color = "White" if winner == "w" else "Black"
        if type == "checkmate":
            _text = f"{color} has won by checkmate"
        elif type == "stalemate":
            _text = "Draw by stalemate"
        else:
            _text = f"{color} has won by resignation!"

        result = Label(root, text=_text)
        result.place(x=(GAME_OVER_WIDTH / 2) - (result.winfo_reqwidth() / 2), y=(GAME_OVER_HEIGHT / 2) - (result.winfo_reqheight() / 2))

        # restart_btn = Button(root, text="New game", command=lambda: self.reset_win(root))
        # restart_btn.pack(ipadx=5, ipady=5)

        root.mainloop()

    def change_piece_type(self, piece, choice, r, c, row, col):
        global root, running
        running = False
        root.destroy()
        piece.piece_type = choice
        self.s.sendall(f"Moved: {r},{c},{row},{col}".encode())
        self.s.sendall(f"Change: {row},{col},{choice}".encode())

    def promotion(self, piece, r, c, row, col):
        global root, running
        running = True
        while running:
            root = Tk()
            root.title("Pawn promotion")
            root.iconbitmap(ICON_PATH_ICO)
            root.resizable(False, False)
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()
            x = (screen_width/2) - (PROMOTION_WIDTH/2)
            y = (screen_height/2) - (PROMOTION_HEIGHT/2)
            root.geometry(f"{PROMOTION_WIDTH}x{PROMOTION_HEIGHT}+{int(x)}+{int(y)}")

            queen_img = PhotoImage(file=PIECE_PATH.replace("x", f"{piece.color}_queen"))
            rook_img = PhotoImage(file=PIECE_PATH.replace("x", f"{piece.color}_rook"))
            bishop_img = PhotoImage(file=PIECE_PATH.replace("x", f"{piece.color}_bishop"))
            knight_img = PhotoImage(file=PIECE_PATH.replace("x", f"{piece.color}_knight"))

            queen_btn = Button(root, image=queen_img, width=144, height=PROMOTION_HEIGHT, command=lambda: self.change_piece_type(piece, "queen", r, c, row, col))
            rook_btn = Button(root, image=rook_img, width=144, height=PROMOTION_HEIGHT, command=lambda: self.change_piece_type(piece, "rook", r, c, row, col))
            bishop_btn = Button(root, image=bishop_img, width=144, height=PROMOTION_HEIGHT, command=lambda: self.change_piece_type(piece, "bishop", r, c, row, col))
            knight_btn = Button(root, image=knight_img, width=144, height=PROMOTION_HEIGHT, command=lambda: self.change_piece_type(piece, "knight", r, c, row, col))

            queen_btn.grid(row=0, column=0)
            rook_btn.grid(row=0, column=1)
            bishop_btn.grid(row=0, column=2)
            knight_btn.grid(row=0, column=3)

            root.mainloop()