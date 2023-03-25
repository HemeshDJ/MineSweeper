#!/usr/bin/env python

import pygame
from src.Board import Board
import logging
from src.gamemode import gamemode as gm
from src.Draw import Draw, WHITE

# MineSweeper Game

# 1. Create a grid of squares
# 2. Place bombs randomly on the grid
# 3. Place numbers on the grid
# 4. Allow the user to click on a square
# 5. If the user clicks on a bomb, the game is over
# 6. If the user clicks on a number, show the number
# 7. If the user clicks on a blank square, show all adjacent blank squares
# 8. If the user clicks on a square with the correct number of flags around it, show all adjacent squares
# 9. Allow the user to flag squares they think are bombs
# 10. If the user flags all the bombs, they win

# Initialize the logger
logging.basicConfig(filename="log.txt", level=logging.DEBUG, format="%(asctime)s:%(levelname)s:%(message)s")

# Initialize the board
board = Board()
logging.info("[+] Board initialized")

# Initialize the game engine
pygame.init()
logging.info("[+] Pygame initialized")

settings = {
    'mode': 'Beginner',
    'deterministic': True
}

board.new_board(gm[settings['mode']]["grid"], gm[settings['mode']]["bombs"])

# Set the height and width of the screen
screen = pygame.display.set_mode(gm[settings['mode']]["size"])
logging.info("[+] Screen initialized")

# Set the title of the window
pygame.display.set_caption("Minesweeper - " + settings['mode'] + " " + str(board.flags) + "/" + str(board.bombs))
 
# Useful variables
size = gm[settings['mode']]["size"]
grid_size = gm[settings['mode']]["grid_size"]
grid_start_location = (100 + (size[0] - grid_size[0]) // 2, (size[1] - grid_size[1]) // 2)
grid_end_location = (grid_start_location[0] + grid_size[0], grid_start_location[1] + grid_size[1])

def change_mode(new_mode):
    """
    Changes the mode of the game
    """
    settings["mode"] = new_mode
    pygame.display.set_mode(gm[new_mode]["size"])
    board.new_board(gm[new_mode]["grid"], gm[new_mode]["bombs"])

    global size, grid_size, grid_start_location, grid_end_location  
    size = gm[new_mode]["size"]
    grid_size = gm[new_mode]["grid_size"]
    grid_start_location = (100 + (size[0] - grid_size[0]) // 2, (size[1] - grid_size[1]) // 2)
    grid_end_location = (grid_start_location[0] + grid_size[0], grid_start_location[1] + grid_size[1])

    logging.info("Mode changed to " + new_mode)

def get_grid_pos(pos):
    """
    Returns the grid position of a mouse click
    """
    grid = board.grid

    start_x = grid_start_location[0]
    end_x = grid_end_location[0]
    len_x = (end_x - start_x) // grid[0]

    start_y = grid_start_location[1]
    end_y = grid_end_location[1]
    len_y = (end_y - start_y) // grid[1]

    if pos[0] < start_x or pos[0] > end_x or pos[1] < start_y or pos[1] > end_y:
        return None
    
    x = (pos[0] - start_x) // len_x
    y = (pos[1] - start_y) // len_y

    if x >= grid[0] or y >= grid[1]:
        return None

    return (x, y)

# Loop until the user clicks the close button.
done = False
clock = pygame.time.Clock()

current_time = 0

# -------- Main Program Loop -----------
while not done:
    # --- Main event loop
    for event in pygame.event.get(): # User did something
        if event.type == pygame.QUIT: # If user clicked close
            done = True # Flag that we are done so we exit this loop

        # User clicks the mouse. Get the position
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            grid_pos = get_grid_pos(pos)
            
            logging.debug("Mouse click at: " + str(pos) + "{" + str(grid_pos) + "}")

            if grid_pos is None:
                continue

            if board.game_over or board.won:
                continue

            # left click to reveal_square, right click to flag_square
            if event.button == 1:
                board.reveal_square(grid_pos)
            elif event.button == 3:
                board.flag_square(grid_pos)

            board.check_win()

        # User presses a key
        if event.type == pygame.KEYDOWN:
            logging.debug("Key pressed: " + str(event.key))

            if event.key == pygame.K_SPACE:
                board.new_board(board.grid, board.bombs)

            if event.key == pygame.K_r:
                board.reveal_all()

            if event.key == pygame.K_u:
                board.unreveal_all()

            if event.key == pygame.K_s:
                board.save_board()

            if event.key == pygame.K_l:
                board.load_board()

            if event.key == pygame.K_q:
                done = True

            if event.key == pygame.K_b:
                change_mode("Beginner")

            if event.key == pygame.K_i:
                change_mode("Intermediate")

            if event.key == pygame.K_e:
                change_mode("Expert")

            if event.key == pygame.K_d:
                settings["deterministic"] = not settings["deterministic"]

    # --- Game logic should go here
    pygame.display.set_caption("Minesweeper - " + settings['mode'] + " " + str(board.flags) + "/" + str(board.bombs))

    # --- Drawing code should go here
    # First, clear the screen to white. Don't put other drawing commands
    # above this, or they will be erased with this command.
    screen.fill(WHITE)

    Draw().draw(screen, board, settings)

    # --- Go ahead and update the screen with what we've drawn.
    pygame.display.update()

    # --- Limit to 60 frames per second
    clock.tick(60)

# Close the window and quit.
pygame.quit()
