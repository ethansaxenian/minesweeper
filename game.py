import enum
from typing import Optional, Tuple

from board import Board


class Action(enum.Enum):
    UNCOVER = 1
    FLAG = 2
    UNFLAG = 3
    GIVE_UP = 4


def get_difficulty() -> int:
    difficulty = input('choose your difficulty: 1 = easy, 2 = intermediate, 3 = hard: ')
    while True:
        if difficulty.isnumeric() and int(difficulty) in (1, 2, 3):
            return int(difficulty)
        difficulty = input('invalid input, try again: ')


def print_board(board: Board):
    print(f'\n{board.covered_bombs} covered bombs left\n')
    print(board)
    print("type 'r x y' to reveal cell at row x, column y")
    print("type 'f x y' to flag cell at row x, column y")
    print("type 'u x y' to remove flag at row x, column y")
    print("type 'e' to give up")


def parse_user_input(user_input: str, board: Board) -> Optional[Tuple[Action, Optional[int], Optional[int]]]:
    split_list = user_input.split(" ")
    if split_list[0] == 'r':
        if len(split_list) != 3:
            return None
        try:
            row = int(split_list[1])
            col = int(split_list[2])
        except ValueError:
            return None
        if not (board.valid_row(row) and board.valid_column(col)):
            return None
        if board.valid_uncover(row, col):
            return Action.UNCOVER, row, col
    elif split_list[0] == 'f':
        if len(split_list) != 3:
            return None
        try:
            row = int(split_list[1])
            col = int(split_list[2])
        except ValueError:
            return None
        if not (board.valid_row(row) and board.valid_column(col)):
            return None
        if board.valid_flag(row, col):
            return Action.FLAG, row, col
    elif split_list[0] == 'u':
        if len(split_list) != 3:
            return None
        try:
            row = int(split_list[1])
            col = int(split_list[2])
        except ValueError:
            return None
        if not (board.valid_row(row) and board.valid_column(col)):
            return None
        if board.valid_unflag(row, col):
            return Action.UNFLAG, row, col
    elif split_list[0] == 'e':
        if len(split_list) != 1:
            return None
        return Action.GIVE_UP, None, None
    else:
        return None


def get_move(board: Board) -> Tuple[Action, Optional[int], Optional[int]]:
    user_input = input('make a move: ')
    while True:
        action = parse_user_input(user_input, board)
        if action is not None:
            return action
        user_input = input('invalid input, try again: ')


def make_move(move: Tuple[Action, int, int], board: Board):
    action, row, col = move[0], move[1], move[2]
    if action == Action.UNCOVER:
        board.uncover(row, col)
    elif action == Action.FLAG:
        board.flag(row, col)
    elif action == Action.UNFLAG:
        board.unflag(row, col)


def main():
    print('Welcome to Minesweeper')
    difficulty = get_difficulty()
    board = Board(difficulty)
    while True:
        print_board(board)
        move = get_move(board)
        if move[0] == Action.GIVE_UP:
            board.reveal_mines()
            print('\nYou lose!')
            break
        else:
            make_move(move, board)
            if move[0] == Action.UNCOVER and board.bomb(move[1:]):
                board.reveal_mines()
                print('\nYou lose!')
                break
            if board.player_win():
                print(board)
                print('\nYOU WIN!!!')
                break


if __name__ == '__main__':
    main()
