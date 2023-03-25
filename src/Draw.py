import pygame
from .colors import *
from .gamemode import gamemode

class Draw:
    def __init__(self):
        pass

    def draw(self, screen, board, settings):
        self.screen = screen
        self.mode = settings["mode"]
        self.board = board
        self.settings = settings

        self.size = gamemode[self.mode]["size"]
        self.grid_size = gamemode[self.mode]["grid_size"]
        self.grid_start_location = (100 + (self.size[0] - self.grid_size[0]) // 2, (self.size[1] - self.grid_size[1]) // 2)
        self.grid_end_location = (self.grid_start_location[0] + self.grid_size[0], self.grid_start_location[1] + self.grid_size[1])

        self.draw_instructions()
        self.draw_labels()
        self.draw_grid()

        self.display_timer()

    def display_timer(self):
        """
        Creates and displays the timer
        """
        font = pygame.font.SysFont('Arial', 40)
        if self.board.game_over or self.board.won:
            start = self.board.start_time
            end = self.board.end_time
            time = (end - start) / 1000
        elif self.board.start_time is not None:
            start = self.board.start_time
            current = pygame.time.get_ticks()
            time = (current - start) / 1000
        else:
            time = 0

        text = font.render("{0:.2f} s".format(time).zfill(8), True, BLUE)
        self.screen.blit(text, [50, self.grid_start_location[1] + 10])

    def draw_instructions(self):
        """
        Draws the instructions
        """
        font = pygame.font.SysFont('Comic Sans MS', 30)
        height = font.get_height() * 3

        text = font.render("Left Click - Reveal", True, BLACK)
        self.screen.blit(text, [25, self.grid_start_location[1] + 100 + height * 1 // 2 + 10])

        text = font.render("Right Click - Flag", True, BLACK)
        self.screen.blit(text, [25, self.grid_start_location[1] + 100 + height * 3 // 2 + 10])

        text = font.render("SPACE - RESET", True, BLACK)
        self.screen.blit(text, [25, self.grid_start_location[1] + 100 + height * 5 // 2 + 10])

        text = font.render("Q - Quit", True, BLACK)
        self.screen.blit(text, [25, self.grid_start_location[1] + 100 + height * 7 // 2 + 10])

    def draw_labels(self):
        """
        Draws the labels
        """
        if self.board.game_over:
            # Draw the text "Game Over"
            font = pygame.font.SysFont('Calibri', 25, True, False)
            text = font.render("Game Over", True, BLACK)
            self.screen.blit(text, [self.grid_start_location[0] + self.grid_size[0] // 2 - text.get_width() // 2, self.grid_start_location[1] - 25])

        if self.board.won:
            # Draw the text "You Won"
            font = pygame.font.SysFont('Calibri', 25, True, False)
            text = font.render("You Won", True, BLACK)
            self.screen.blit(text, [self.grid_start_location[0] + self.grid_size[0] // 2 - text.get_width() // 2, self.grid_start_location[1] - 25])

    def draw_grid(self):
        """
        Draws the grid
        """
        grid = self.board.grid

        start_x = self.grid_start_location[0]
        end_x = self.grid_end_location[0]
        len_x = (end_x - start_x) // grid[0]

        start_y = self.grid_start_location[1]
        end_y = self.grid_end_location[1]
        len_y = (end_y - start_y) // grid[1]

        for i in range(grid[0]):
            for j in range(grid[1]):
                if self.board.start_pos is not None and self.board.start_pos == (i, j):
                    pygame.draw.rect(self.screen, GREEN, (start_x + i * len_x, start_y + j * len_y, len_x, len_y))
                elif self.board.board[i][j].bomb and (self.board.board[i][j].revealed or self.board.game_over):
                    pygame.draw.rect(self.screen, DARK_RED, (start_x + i * len_x, start_y + j * len_y, len_x, len_y))
                elif self.board.board[i][j].flagged:
                    pygame.draw.rect(self.screen, LIGHT_RED, (start_x + i * len_x, start_y + j * len_y, len_x, len_y))
                elif not self.board.board[i][j].revealed:
                    pygame.draw.rect(self.screen, DARK_GREY, (start_x + i * len_x, start_y + j * len_y, len_x, len_y))
                elif self.board.start_pos is not None and self.board.start_pos == (i, j):
                    pygame.draw.rect(self.screen, GREEN, (start_x + i * len_x, start_y + j * len_y, len_x, len_y))
                else:
                    pygame.draw.rect(self.screen, LIGHT_GREY, (start_x + i * len_x, start_y + j * len_y, len_x, len_y))
                    if self.board.board[i][j].value > 0:
                        font = pygame.font.SysFont('Calibri', 25, True, False)
                        text = font.render(str(self.board.board[i][j].value), True, BLACK)
                        self.screen.blit(text, [start_x + i * len_x + len_x // 2 - text.get_width() // 2, start_y + j * len_y + len_y // 2 - text.get_height() // 2])

        for x in range(start_x, end_x + 1, len_x):
            pygame.draw.line(self.screen, WHITE, (x, start_y), (x, end_y), 2)
        for y in range(start_y, end_y + 1, len_y):
            pygame.draw.line(self.screen, WHITE, (start_x, y), (end_x, y), 2)