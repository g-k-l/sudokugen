
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from itertools import product
import math
import sqlite3
import sys

import numpy as np
from numpy.random import shuffle


conn = sqlite3.connect('sudoku.db')


def setup_db(conn):
    template = '"{}" integer,'
    columns = "\n".join(
        [template.format(n) for n in range(80)] + ['"80" integer'])
    # final_col = "80 integer"

    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS solutions (
        id SERIAL PRIMARY KEY,
        {});""".format(columns))
    conn.commit()


BOARD_DIM = 9
REP_UNFILLED_SQUARE = 0
COMPLETE_ROW = set(range(1, BOARD_DIM+1))


class Board(object):
    def __init__(self, board):
        self.board = board
        self.finished = False


def is_filled(board):
    if np.count_nonzero(board) == BOARD_DIM**2:
        return True
    return False


def process_solution(bc):
    c = conn.cursor()
    c.execute("INSERT INTO solutions VALUES {};".format(
        tuple(bc.board.flatten())))
    conn.commit()
    bc.finished = True
    return bc


def squares():
    groups = defaultdict(set)
    lookup = defaultdict(int)
    data = [
        (3, 3, 0),
        (6, 3, 1),
        (9, 3, 2),
        (3, 6, 3),
        (6, 6, 4),
        (9, 6, 5),
        (3, 9, 6),
        (6, 9, 7),
        (9, 9, 8),
    ]
    for position in range(BOARD_DIM**2):
        x = position % BOARD_DIM
        y = math.floor(position / BOARD_DIM)
        for xlim, ylim, g in data:
            if x < xlim and y < ylim:
                groups[g].add((x, y))
                lookup[(x, y)] = g
                break
    return groups, lookup


def choices_from_square(board, x, y):
    groups, lookup = squares()
    g = lookup[(x, y)]
    cells_in_g = groups[g]
    numbers_in_g = {board[a, b] for a, b in cells_in_g}
    # print("================")
    # print(g)
    # print(cells_in_g)
    # print(numbers_in_g)
    return COMPLETE_ROW - numbers_in_g


def construct_candidates(board, x, y):
    possible_from_row = COMPLETE_ROW - set(board[x, :])
    possible_from_col = COMPLETE_ROW - set(board[:, y])
    possible_from_square = choices_from_square(board, x, y)
    # print("================")
    # print(board)
    # print("x: ", x)
    # print("y: ", y)
    # print(possible_from_col & possible_from_row & possible_from_square)
    return possible_from_col & possible_from_row & possible_from_square


# def backtrack(bc, positions):
#     board = bc.board
#     print(positions)

#     if is_a_solution(board):
#         return process_solution(bc)

#     x = positions[0] % BOARD_DIM
#     y = math.floor(positions[0] / BOARD_DIM)

#     candidates = construct_candidates(board, x, y)

#     for candidate in candidates:
#         board[x, y] = candidate
#         backtrack(bc, positions[0:])
#         if bc.finished:
#             return bc
#         board[x, y] = REP_UNFILLED_SQUARE


def get_unfilled_cell_rand(board):
    zero_indices = np.argwhere(board == 0)
    if len(zero_indices) > 0:
        cell_index = np.random.randint(len(zero_indices))
    else:
        cell_index = zero_indices[0]
    x, y = zero_indices[cell_index]
    return x, y

    # while True:
    #     x = np.random.randint(9)
    #     y = np.random.randint(9)
    #     if board[x, y] == 0:
    #         return x, y


def backtrack_iter(board):
    stack = [board]
    while True:
        if is_filled(board):
            return board
        board = stack.pop()
        x, y = get_unfilled_cell_rand(board)
        sys.stdout.write("# filled: {}\r".format(np.count_nonzero(board)))
        sys.stdout.flush()
        if np.count_nonzero(board) > 75:
            print(board)

        candidates = construct_candidates(board, x, y)
        # print(candidates)
        for candidate in candidates:
            copied = board.copy()
            copied[x, y] = candidate
            stack.append(copied)


# backtrack(bc, positions[0:])
# if is_a_solution(board):
#     return bc

# board[x, y] = REP_UNFILLED_SQUARE

# return bc


if __name__ == "__main__":
    setup_db(conn)

    n_jobs = 1
    n_workers = 1

    starting_boards = [
        Board(board=np.zeros((BOARD_DIM, BOARD_DIM,), dtype=int))
        for __ in range(n_jobs)]
    positions_remainings = [
        np.arange(BOARD_DIM**2, dtype=int) for __ in range(n_jobs)]
    __ = [shuffle(arr) for arr in positions_remainings]
    positions_remainings = [list(arr) for arr in positions_remainings]

    # initial_data = zip(starting_boards, positions_remainings)

    print(backtrack_iter(starting_boards[0].board))

    # with ProcessPoolExecutor(max_workers=n_workers) as executor:
    #     for bc in zip(initial_data, executor.map(backtrack, initial_data)):
    #         # TODO: anything important to do here?
    #         print(bc)
