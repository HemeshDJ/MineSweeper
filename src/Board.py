import random
import copy
import logging

class Board:
    class Square:
        def __init__(self, value):
            self.value = value
            self.revealed = False
            self.flagged = False

            self.bomb = (self.value == -1)
            self.display = (self.value != 0)

            self.revealed_adjacent = False

        def __str__(self):
            return str(self.value)
        
        def reveal(self):
            self.revealed = True

        def unreveal(self):
            self.revealed = False

        def flag(self):
            self.flagged = True

        def unflag(self):
            self.flagged = False

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
                board[i].append(self.Square(0))
        
        # Choose random locations for bombs
        bomb_indices = [(i // grid[1], i % grid[1]) for i in range(grid[0] * grid[1])]
        random.shuffle(bomb_indices)
        bomb_indices = bomb_indices[:bombs]

        # Place bombs on board
        for i in bomb_indices:
            board[i[0]][i[1]] = self.Square(-1)
                
        # Place numbers on board
        for i in range(grid[0]):
            for j in range(grid[1]):
                if not board[i][j].bomb:
                    board[i][j] = self.Square(self.__get_number(board, i, j))

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
    
    def new_board(self, grid, bombs):
        """
        Creates a new board
        """
        self.grid = grid
        self.bombs = bombs
        self.board = self.create_board(grid, bombs)
        self.flags = 0
        self.game_over = False
        self.won = False

    def reveal_square(self, pos):
        """
        Reveals a square
        """
        square = self.board[pos[0]][pos[1]] 
        if square.flagged:
            return
        elif not square.revealed:
            square.reveal()
            if square.bomb:
                self.game_over = True
            elif not square.display and not square.revealed_adjacent:
                square.revealed_adjacent = True
                self.reveal_adjacent(pos)
        else:
            if self.checksum(pos) and not square.revealed_adjacent:
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
                    square = self.board[x][y]
                    if square.flagged:
                        continue
                    elif not square.revealed:
                        square.reveal()
                        if square.bomb:
                            self.game_over = True
                        elif not square.display and not square.revealed_adjacent:
                            square.revealed_adjacent = True
                            self.reveal_adjacent(pos)

    def flag_square(self, pos):
        """
        Flags a square
        """
        if self.flags >= self.bombs:
            logging.info("No more flags available")
        elif not self.board[pos[0]][pos[1]].revealed:
            if self.board[pos[0]][pos[1]].flagged:
                self.board[pos[0]][pos[1]].unflag()
                self.flags -= 1
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
                        number += 1
        return (number == self.board[pos[0]][pos[1]].value)
    
    def check_win(self):
        """
        Checks if the player has won
        """
        flags_and_bombs = True
        for i in range(self.grid[0]):
            for j in range(self.grid[1]):
                if self.board[i][j].flagged and not self.board[i][j].bomb:
                    flags_and_bombs = False
                elif self.board[i][j].bomb and not self.board[i][j].flagged:
                    flags_and_bombs = False

        reveals_and_bombs = True
        for i in range(self.grid[0]):
            for j in range(self.grid[1]):
                if not self.board[i][j].revealed and not self.board[i][j].bomb:
                    reveals_and_bombs = False
        
        self.won = (flags_and_bombs or reveals_and_bombs)

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
            print("[-] No saved boards")
