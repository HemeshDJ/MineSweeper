import random
import copy
import logging
import pygame

class Board:
    class Square:
        def __init__(self, pos, value):
            self.pos = pos

            self.value = value
            self.revealed = False
            self.flagged = False

            self.bomb = (self.value == -1)
            self.open = not self.bomb
            self.display = (self.value != 0)

            self.revealed_adjacent = False

        def __str__(self):
            return str(self.value)
        
        def reveal(self):
            self.revealed = True
            logging.debug("[+] Square at " + str(self.pos) + " revealed (value: " + str(self.value) + ")")

        def unreveal(self):
            self.revealed = False
            logging.debug("[+] Square at " + str(self.pos) + " unrevealed")

        def flag(self):
            self.flagged = True
            logging.debug("[+] Square at " + str(self.pos) + " flagged")

        def unflag(self):
            self.flagged = False
            logging.debug("[+] Square at " + str(self.pos) + " unflagged")

    def __init__(self):
        self.saved_boards = []
        pass

    def __str__(self):
        return str(self.board)

    def create_board(self, grid, bombs):
        """
        Creates a board with bombs and numbers
        """
        # Create empty board
        board = []
        for i in range(grid[0]):
            board.append([])
            for j in range(grid[1]):
                board[i].append(self.Square((i, j), 0))
        
        # Choose random locations for bombs
        bomb_indices = [(i // grid[1], i % grid[1]) for i in range(grid[0] * grid[1])]
        random.shuffle(bomb_indices)
        bomb_indices = bomb_indices[:bombs]

        # Place bombs on board
        for i in bomb_indices:
            board[i[0]][i[1]] = self.Square(i, -1)
            
        for i in bomb_indices:
            for x in range(i[0] - 1, i[0] + 2):
                for y in range(i[1] - 1, i[1] + 2):
                    if x < 0 or x >= len(board) or y < 0 or y >= len(board[0]):
                        continue
                    else:
                        if not board[x][y].bomb:
                            board[x][y].value += 1

        logging.info("[+] Board created")
        return board
    
    def __get_number(self, board, i, j):
        """
        Returns the number of bombs surrounding a square
        """
        number = 0
        for x in range(i - 1, i + 2):
            for y in range(j - 1, j + 2):
                if x < 0 or x >= len(board) or y < 0 or y >= len(board[0]):
                    continue
                else:
                    if board[x][y].bomb:
                        number += 1
        return number
    
    def new_board(self, grid, bombs, deterministic=False):
        """
        Creates a new board
        """
        self.grid = grid
        self.bombs = bombs
        self.board = self.create_board(grid, bombs)
        self.start_pos = None
        self.isdeterministic = deterministic
        while deterministic and self.deterministic():
            logging.info("[-] Board is not deterministic")
            self.board = self.create_board(grid, bombs)
        self.flags = 0
        self.game_over = False
        self.won = False
        self.playing = False
        self.start_time = None
        self.end_time = None

        logging.info("[+] New board created (grid: " + str(grid) + ", bombs: " + str(bombs) + " deterministic: " + str(deterministic) + ")")

    def deterministic(self):
        """
        Checks if the board is deterministic
        """
        self.start_pos = (random.randint(0, self.grid[0] - 1), random.randint(0, self.grid[1] - 1))

        # Check if the start position is a bomb
        while self.board[self.start_pos[0]][self.start_pos[1]].bomb or self.board[self.start_pos[0]][self.start_pos[1]].value != 0:
            self.start_pos = (random.randint(0, self.grid[0] - 1), random.randint(0, self.grid[1] - 1))
        
        # Create a board to solve
        # '?' = unrevealed
        # -1 = bomb
        # 0..8 = revealed
        self.board_to_solve = []
        for i in range(self.grid[0]):
            self.board_to_solve.append([])
            for j in range(self.grid[1]):
                self.board_to_solve[i].append('?')

        # Perform a depth-first search
        stack = [self.start_pos]
        to_check = []
        visited = []
        while stack:
            pos = stack.pop()
            if pos in visited:
                continue
            visited.append(pos)
            self.board_to_solve[pos[0]][pos[1]] = self.board[pos[0]][pos[1]].value
            for x in range(pos[0] - 1, pos[0] + 2):
                for y in range(pos[1] - 1, pos[1] + 2):
                    if x < 0 or x >= len(self.board) or y < 0 or y >= len(self.board[0]):
                        continue
                    elif (x, y) not in visited:
                        if self.board[x][y].value != 0:
                            stack.append((x, y))
                        else:
                            to_check.append((x, y))

        # Perform a breadth-first search
        while to_check:
            to_check_next = []
            while to_check:
                pos = to_check.pop(0)
                if pos in visited:
                    continue
                visited.append(pos)
                self.board_to_solve[pos[0]][pos[1]] = self.board[pos[0]][pos[1]].value
                number = 0
                for x in range(pos[0] - 1, pos[0] + 2):
                    for y in range(pos[1] - 1, pos[1] + 2):
                        if x < 0 or x >= len(self.board) or y < 0 or y >= len(self.board[0]):
                            continue
                        elif self.board_to_solve[x][y] == '?' or self.board_to_solve[x][y] == -1:
                            number += 1
                if number == self.board[pos[0]][pos[1]].value:
                    for x in range(pos[0] - 1, pos[0] + 2):
                        for y in range(pos[1] - 1, pos[1] + 2):
                            if x < 0 or x >= len(self.board) or y < 0 or y >= len(self.board[0]):
                                continue
                            elif self.board_to_solve[x][y] == '?':
                                self.board_to_solve[x][y] = -1
                                to_check_next.append((x, y))
            to_check = to_check_next

        # Check if the board is deterministic
        for i in range(self.grid[0]):
            for j in range(self.grid[1]):
                if self.board_to_solve[i][j] == '?' and not self.board[i][j].bomb:
                    return False
        return True

    def reveal_square(self, pos):
        """
        Reveals a square
        """
        if not self.playing:
            self.playing = True
            self.start_time = pygame.time.get_ticks()
            
        square = self.board[pos[0]][pos[1]]
        if square.flagged:
            return
        elif not square.revealed:
            square.reveal()
            if square.bomb:
                self.game_over = True
                self.end_time = pygame.time.get_ticks()
                logging.info("[-] Game over")
            elif square.value == 0 and not square.revealed_adjacent:
                square.revealed_adjacent = True
                self.reveal_adjacent(pos)
        elif self.checksum(pos) and not square.revealed_adjacent:
            square.revealed_adjacent = True
            self.reveal_adjacent(pos)

    def reveal_adjacent(self, pos):
        """
        Reveals all adjacent squares
        """
        for x in range(pos[0] - 1, pos[0] + 2):
            for y in range(pos[1] - 1, pos[1] + 2):
                if x < 0 or x >= len(self.board) or y < 0 or y >= len(self.board[0]):
                    continue
                else:
                    if not self.board[x][y].revealed:
                        self.reveal_square((x, y))

    def flag_square(self, pos):
        """
        Flags a square
        """
        if not self.board[pos[0]][pos[1]].revealed:
            if self.board[pos[0]][pos[1]].flagged:
                self.board[pos[0]][pos[1]].unflag()
                self.flags -= 1
            elif self.flags >= self.bombs:
                logging.info("[-] No more flags available")
            else:
                self.board[pos[0]][pos[1]].flag()
                self.flags += 1

    def checksum(self, pos):
        """
        Checks if the number of flagged squares around a revealed square is equal to the value of the square
        """
        number = 0
        for x in range(pos[0] - 1, pos[0] + 2):
            for y in range(pos[1] - 1, pos[1] + 2):
                if x < 0 or x >= len(self.board) or y < 0 or y >= len(self.board[0]):
                    continue
                else:
                    if self.board[x][y].flagged:
                        if not self.board[x][y].bomb:
                            self.game_over = True
                            self.end_time = pygame.time.get_ticks()
                            return False
                        number += 1
        return (number == self.board[pos[0]][pos[1]].value)
    
    def check_win(self):
        """
        Checks if the player has won
        """
        reveals_and_bombs = True
        for i in range(self.grid[0]):
            for j in range(self.grid[1]):
                if not self.board[i][j].revealed and not self.board[i][j].bomb:
                    reveals_and_bombs = False
        
        self.won = reveals_and_bombs

        if self.won:
            self.end_time = pygame.time.get_ticks()

    def reveal_all(self):
        """
        Reveals all squares
        """
        for i in range(self.grid[0]):
            for j in range(self.grid[1]):
                self.board[i][j].reveal()

    def unreveal_all(self):
        """
        Unreveals all squares
        """
        for i in range(self.grid[0]):
            for j in range(self.grid[1]):
                self.board[i][j].unreveal()

    def flag_all(self):
        """
        Flags all bombs
        """
        for i in range(self.grid[0]):
            for j in range(self.grid[1]):
                if self.board[i][j].bomb:
                    self.board[i][j].flag()

    def unflag_all(self):
        """
        Unflags all squares
        """
        for i in range(self.grid[0]):
            for j in range(self.grid[1]):
                self.board[i][j].unflag()

    def save_board(self):
        """
        Saves the board to a stack
        """
        self.saved_boards.append(copy.deepcopy(self.board))

    def load_board(self):
        """
        Loads the board from a stack
        """
        if self.saved_boards:
            self.board = self.saved_boards.pop()
        else:
            logging.error("[-] No saved boards")
