import numpy as np
import pygame
import sys
import math
import random

BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

ROW_COUNT = 6
COLUMN_COUNT = 7

def create_board():
    board = np.zeros((ROW_COUNT, COLUMN_COUNT))
    return board


def drop_piece(board, row, column, piece):
    board[row][column] = piece


def is_valid_location(board, column):
    return board[ROW_COUNT - 1][column] == 0


def get_next_open_row(board, column):
    for r in range(ROW_COUNT):
        if board[r][column] == 0:
            return r


def print_board(board):
    print(np.flip(board, 0))


def winning_move(board, piece):
    # Check horizontal locations for a win
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT):
            if board[r][c] == piece and board[r][c + 1] == piece and board[r][c + 2] == piece and board[r][
                c + 3] == piece:
                return True

    # Check vertical locations for a win
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT-3):
            if board[r][c] == piece and board[r + 1][c] == piece and board[r + 2][c] == piece and board[r + 3][
                c] == piece:
                return True

    # Check for positively sloped diagonal

    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT - 3):
            if board[r][c] == piece and board[r + 1][c + 1] == piece and board[r + 2][c + 2] == piece and board[r + 3][
                c + 3] == piece:
                return True

    # Check for negatively sloped diagonals

    for c in range(COLUMN_COUNT - 3):
        for r in range(3, ROW_COUNT):
            if board[r][c] == piece and board[r - 1][c + 1] == piece and board[r - 2][c + 2] == piece and board[r - 3][
                c + 3] == piece:
                return True

def draw_board(board):
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, BLUE, (c*SQUARE_SIZE, r*SQUARE_SIZE + SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            pygame.draw.circle(screen, BLACK, (int(c*SQUARE_SIZE+SQUARE_SIZE/2), int(r*SQUARE_SIZE+SQUARE_SIZE+SQUARE_SIZE/2)), RADIUS)

    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            if board[r][c] == 1:
                pygame.draw.circle(screen, RED, (int(c * SQUARE_SIZE + SQUARE_SIZE / 2), height-int(r * SQUARE_SIZE + SQUARE_SIZE / 2)), RADIUS)
            elif board[r][c] == 2:
                pygame.draw.circle(screen, YELLOW, (int(c * SQUARE_SIZE + SQUARE_SIZE / 2), height-int(r * SQUARE_SIZE + SQUARE_SIZE / 2)), RADIUS)
    pygame.display.update()

# ===================== [ AI SECTION ] =====================

def get_all_valid_location(board):
    valid = []
    for i in range(COLUMN_COUNT):
        if is_valid_location(board, i):
            valid.append(i)
    return valid

def evaluate_window(window, piece):
    score = 0
    turn_now = 1
    if piece == 1:
        turn_now = 2
        
    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(0) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(0) == 2:
        score += 2
    if window.count(piece) == 3 and window.count(0) == 1:
        score -= 4
        
    return score

# test heuristic #1
def calculate_score_based_position(board, piece):
    score = 0
    
    ## Score center column
    center_array = [int(i) for i in list(board[:, COLUMN_COUNT//2])]
    center_count = center_array.count(piece)
    score += center_count * 3
    
    ## Score Horizontal
    for r in range(ROW_COUNT):
        row_array = [int(i) for i in list(board[r,:])]
        for c in range(COLUMN_COUNT-3):
            window = row_array[c:c+4]
            score += evaluate_window(window, piece)

    ## Score Vertical
    for c in range(COLUMN_COUNT):
        col_array = [int(i) for i in list(board[:,c])]
        for r in range(ROW_COUNT-3):
            window = col_array[r:r+4]
            score += evaluate_window(window, piece)

    ## Score posiive sloped diagonal
    for r in range(ROW_COUNT-3):
        for c in range(COLUMN_COUNT-3):
            window = [board[r+i][c+i] for i in range(4)]
            score += evaluate_window(window, piece)

    for r in range(ROW_COUNT-3):
        for c in range(COLUMN_COUNT-3):
            window = [board[r+3-i][c+i] for i in range(4)]
            score += evaluate_window(window, piece)
            
    return score

def terminal_node(board):
    # 1 = player 1 | 2 = player 2/AI
    return winning_move(board, 1) or winning_move(board, 2) or len(get_all_valid_location(board)) == 0

def minimax(board, depth, alpha, beta, maximizingPlayer):
    all_valid_location = get_all_valid_location(board)
    is_terminal = terminal_node(board)
    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board,2):
                return None, math.inf
            elif winning_move(board,1):
                return None, -math.inf
            else:
                return None, 0
        else:
            return None, calculate_score_based_position(board, 2)
    if maximizingPlayer:
        value = -math.inf
        column = random.choice(all_valid_location)
        for col in all_valid_location:
            row = get_next_open_row(board, col)
            temp_board = board.copy()
            drop_piece(temp_board, row, col, 2)
            new_score = minimax(temp_board, depth - 1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(value, alpha)
            if alpha >= beta:
                break
        return column, value
    else:
        value = math.inf
        column = random.choice(all_valid_location)
        for col in all_valid_location:
            row =  get_next_open_row(board, col)
            temp_board = board.copy()
            drop_piece(temp_board, row, col, 1)
            new_score = minimax(temp_board,depth-1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value
        
board = create_board()
print_board(board)
game_over = False
turn = 0

pygame.init()

SQUARE_SIZE = 120
width = COLUMN_COUNT*SQUARE_SIZE
height = (ROW_COUNT+1)*SQUARE_SIZE

size = (width, height)

RADIUS = int(SQUARE_SIZE/2-5)

screen = pygame.display.set_mode(size)
draw_board(board)
pygame.display.update()

myfont = pygame.font.SysFont("monospace", 75)

while not game_over:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == pygame.MOUSEMOTION:
            pygame.draw.rect(screen, BLACK, (0,0, width, SQUARE_SIZE))
            posx = event.pos[0]
            if turn == 0:
                pygame.draw.circle(screen, RED, (posx, int(SQUARE_SIZE/2)), RADIUS)
            else:
                pygame.draw.circle(screen, YELLOW, (posx, int(SQUARE_SIZE / 2)), RADIUS)
        pygame.display.update()

        if event.type == pygame.MOUSEBUTTONDOWN:
            pygame.draw.rect(screen, BLACK, (0,0, width, SQUARE_SIZE))
            # Ask player 1 input
            if turn == 0:
                posx = event.pos[0]
                column = int(math.floor(posx/SQUARE_SIZE))

                if is_valid_location(board, column):
                    row = get_next_open_row(board, column)
                    drop_piece(board, row, column, 1)

                    if winning_move(board, 1):
                        label = myfont.render("Player 1 wins!", 1, RED)
                        screen.blit(label, (40, 10))
                        game_over = True

            # Ask player 2 input / AI
            #else:
                # col, minimax_score = minimax(board, 5, -math.inf, math.inf, True)
                # if is_valid_location(board, col):
                #     row = get_next_open_row(board, col)
                #     drop_piece(board, row, col, 2)
                #     
                #     if winning_move(board, 2):
                #         label = myfont.render("AI 1 wins!", 1, RED)
                #         screen.blit(label, (5, 10))
                #         game_over = True

                # posx = event.pos[0]
                # column = int(math.floor(posx / SQUARE_SIZE))
                # 
                # if is_valid_location(board, column):
                #     row = get_next_open_row(board, column)
                #     drop_piece(board, row, column, 2)
                # 
                #     if winning_move(board, 2):
                #         label = myfont.render("Player 2 wins!", 1, YELLOW)
                #         screen.blit(label, (40, 10))
                #         game_over = True
            print_board(board)
            draw_board(board)

            turn += 1
            turn = turn % 2

            if game_over:
                pygame.time.wait(3000)

        if turn == 1 and not game_over:
            col, minimax_score = minimax(board, 4, -math.inf, math.inf, True)
            if is_valid_location(board, col):
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, 2)
                
                if winning_move(board, 2):
                    label = myfont.render("AI wins!", 1, RED)
                    screen.blit(label, (5, 10))
                    game_over = True
            
                print_board(board)
                draw_board(board)
    
                turn += 1
                turn = turn % 2
    
                if game_over:
                    pygame.time.wait(3000)