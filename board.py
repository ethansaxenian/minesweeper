import enum
import itertools
import random
from typing import List, Tuple


class CellState(enum.Enum):
    COVERED = 1
    UNCOVERED = 2
    FLAGGED = 3


class Cell:
    def __init__(self):
        self.adjacent_cells = []
        self.adjacent_bombs = 0
        self.state = CellState.COVERED
        self.bomb = False

    def __repr__(self):
        if self.state == CellState.COVERED:
            return '.'
        elif self.state == CellState.UNCOVERED:
            if self.bomb:
                return '*'
            else:
                return str(self.adjacent_bombs) if self.adjacent_bombs > 0 else ' '
        elif self.state == CellState.FLAGGED:
            return '?'

    def count_adjacent_bombs(self):
        self.adjacent_bombs = sum(1 for cell in self.adjacent_cells if cell.bomb)

    def adjacent_covered(self):
        return [cell for cell in self.adjacent_cells if cell.state == CellState.COVERED]

    def uncover(self):
        self.state = CellState.UNCOVERED
        if self.adjacent_bombs == 0 and not self.bomb:
            for cell in self.adjacent_covered():
                cell.uncover()

    def flag(self):
        self.state = CellState.FLAGGED

    def unflag(self):
        self.state = CellState.COVERED


class Board:
    NUM_BOMBS = {1: 10, 2: 40, 3: 99}
    WIDTH = {1: 9, 2: 16, 3: 30}
    HEIGHT = {1: 9, 2: 16, 3: 16}
    DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    def __init__(self, difficulty: int):
        self.num_bombs = self.NUM_BOMBS[difficulty]
        self.covered_bombs = self.num_bombs
        self.width = self.WIDTH[difficulty]
        self.height = self.HEIGHT[difficulty]
        self._board: List[List[Cell]] = self.init_board()
        self.add_bombs()
        self.set_adjacent_cells()

    def __repr__(self):
        rep = '\t'
        for x in range(self.width):
            rep += f'{x}\t'
        rep += '\n'
        for i in range(self.height):
            rep += f'{i}\t'
            for j in range(self.width):
                rep += f'{self._board[i][j]}\t'
            rep += '\n'
        return rep

    def init_board(self) -> List[List[Cell]]:
        board = [[] for _ in range(self.height)]
        for i in range(self.height):
            for _ in range(self.width):
                board[i].append(Cell())
        return board

    def add_bombs(self):
        all_cells = list(itertools.chain.from_iterable(self._board))
        for cell in random.sample(all_cells, self.num_bombs):
            cell.bomb = True

    def set_adjacent_cells(self):
        for i in range(self.height):
            for j in range(self.width):
                cell = self._board[i][j]
                for dir in self.DIRECTIONS:
                    if 0 <= i+dir[0] < self.height and 0 <= j+dir[1] < self.width:
                        cell.adjacent_cells.append(self._board[i+dir[0]][j+dir[1]])
                cell.count_adjacent_bombs()

    def bomb(self, cell: Tuple[int, int]) -> bool:
        return self._board[cell[0]][cell[1]].bomb

    def uncover(self, row: int, col: int):
        self._board[row][col].uncover()

    def valid_uncover(self, row: int, col: int) -> bool:
        return self._board[row][col].state != CellState.UNCOVERED

    def flag(self, row: int, col: int):
        self._board[row][col].flag()
        self.covered_bombs -= 1

    def valid_flag(self, row: int, col: int) -> bool:
        return self._board[row][col].state == CellState.COVERED

    def unflag(self, row: int, col: int):
        self._board[row][col].unflag()
        self.covered_bombs += 1

    def valid_unflag(self, row: int, col: int) -> bool:
        return self._board[row][col].state == CellState.FLAGGED

    def valid_row(self, row: int) -> bool:
        return 0 <= row < self.height

    def valid_column(self, col: int) -> bool:
        return 0 <= col < self.width

    def reveal_mines(self):
        for i in range(self.height):
            for j in range(self.width):
                cell = self._board[i][j]
                if cell.bomb:
                    cell.uncover()
        print('\n', self)

    def player_win(self) -> bool:
        for i in range(self.height):
            for j in range(self.width):
                if self._board[i][j].state == CellState.COVERED:
                    return False
        return True
