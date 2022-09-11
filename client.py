import socket
from _thread import *
import pygame
from player import Player
from tkinter import *
from tkinter import messagebox
from constants import *

pygame.init()

server = socket.gethostname()
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.connect((server, port))
except socket.error as e:
    print(e)

global playing, waiting, p, screen, running
waiting = False
playing = False
running = True

def get_mouse_row_col(pos):
    x, y = pos
    row = y // SQUARE_SIZE - 1
    col = x // SQUARE_SIZE - 1
    return int(row), int(col)


def play(player):
    global waiting, playing, p, screen, running

    label_font = pygame.font.Font("freesansbold.ttf", 70)
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(f"Online Chess Game - Player {player}")
    icon = pygame.image.load(ICON_PATH_PNG)
    pygame.display.set_icon(icon)
    timer = pygame.time.Clock()

    while running:
        screen.fill(WHITE)
        timer.tick(60)

        if not waiting and not playing:
            play_width = WIDTH * (3 / 5)
            play_height = play_width / 3
            play_rect = pygame.draw.rect(screen, GREEN, pygame.Rect((WIDTH / 2) - (play_width / 2), (HEIGHT / 2) - (play_height / 2), play_width, play_height))
            play_text = label_font.render("Play!", True, BLACK)
            screen.blit(play_text, ((WIDTH / 2) - (play_text.get_width() / 2), (HEIGHT / 2) - (play_text.get_height() / 2)))
        elif waiting and not playing:
            waiting_text = label_font.render("Waiting for other player...", True, BLACK)
            screen.blit(waiting_text, ((WIDTH / 2) - (waiting_text.get_width() / 2), (HEIGHT / 2) - (waiting_text.get_height() / 2)))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if playing:
                    if not p.over:
                        root = Tk()
                        root.withdraw()
                        reply = messagebox.askokcancel(f"Online Chess Game - Player {player}", "The game is in progress\nDo you want to forfeit?")
                        print(f"You replied {reply} to a question box")
                        if reply:
                            print("Sending forfeit command...")
                            s.sendall("FORFEIT".encode())
                            running = False
                            break
                    else:
                        running = False
                        break
                else:
                    running = False
                    break

            if event.type == pygame.MOUSEBUTTONDOWN:
                if not waiting:
                    if play_rect.collidepoint(event.pos):
                        print("Sending waiting command...")
                        s.sendall("READY".encode())
                        waiting = True
                if playing:
                    if not p.over:
                        if player == p.int_turn:
                            pos = pygame.mouse.get_pos()
                            row, col = get_mouse_row_col(pos)
                            if -1 < row < 8 and -1 < col < 8:
                                p.select(row, col)
                            else:
                                p.valid_moves = []
                                p.select_frame = None
                                s.sendall("UNSELECT".encode())
        if playing:
            p.update()

        # pygame_widgets.update(events)
        pygame.display.flip()

    print("Closed GUI\nSending kill command...")
    s.sendall("KILL".encode())

player = None
while True:
    try:
        data = s.recv(2048).decode()
        if data:
            print(f"Received: {data}")
            if "Player:" in data:
                player = int(data.split(" ")[1])
                print(f"You're player {str(player)}")
                start_new_thread(play, (player, ))
            elif data == "QUIT":
                print("Received a quit command")
                break
            elif data == "PLAY":
                print("Received play command")
                p = Player(screen, s, player)
                playing = True
            elif "Moved:" in data:
                print(f"Received opponent move: {data}")
                start_row, start_col, end_row, end_col = data.split("Moved: ")[1].split(",")
                start_row, start_col, end_row, end_col = ROWS - (int(start_row) + 1), ROWS - (int(start_col) + 1), COLS - (int(end_row) + 1), COLS - (int(end_col) + 1)
                p.selected = p.board.get_piece(start_row, start_col)
                print(f"Moving the piece from {start_row}, {start_col} to {end_row}, {end_col}...")
                p._move(int(end_row), int(end_col))
            elif "Selected:" in data:
                print(f"Opponent select message received: {data}")
                select_coords = data.split("Selected: ")[1]
                select_row, select_col = int(select_coords.split(",")[0]), int(select_coords.split(",")[1])
                select_row, select_col = ROWS - (select_row + 1), COLS - (select_col + 1)
                p.select_frame = (select_row, select_col)
                print(f"Selected a piece at: {select_row}, {select_col}")
                p.valid_moves = p.board.get_valid_moves(p.board.get_piece(select_row, select_col), p.turn)
            elif "Change:" in data:
                print("Opponent did a promotion\nChange piece type...")
                prom_row, prom_col, prom_choice = data.split("Change: ")[1].split(",")
                prom_row, prom_col = int(ROWS - (int(prom_row) + 1)), int(COLS - (int(prom_col) + 1))
                piece = p.board.get_piece(prom_row, prom_col)
                print(prom_row, prom_col, prom_choice)
                print(type(prom_row), type(prom_col), type(prom_choice))
                piece.piece_type = prom_choice
            elif data == "FORFEIT":
                print("Opponent surrendered\nYou won the game!")
                p.game_over(p.turns[player], "forfeit")
            elif data == "UNSELECT":
                print("Received unselect command\nUnselecting...")
                p.select_frame = None
                p.valid_moves = []
        else:
            print("Error while receiving data")
            break
    except Exception as e:
        print(e)
        break

print("Closing connection...")
s.close()