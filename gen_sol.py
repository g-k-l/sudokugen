"""
This file contains a backtracking
sudoku solver for generating fully
-populated puzzles.
"""

from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
import math
import sqlite3
import sys

import numpy as np

from constants import BOARD_DIM, COMPLETE_ROW, DEBUG


conn = sqlite3.connect('sudoku.db')


def setup_db(conn):
    """
    Creates a table "solutions" to store
    generated solutions.
    """
    template = '"{}" integer,'
    columns = "\n".join(
        [template.format(n) for n in range(80)] + ['"80" integer'])

    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS solutions (
        {});""".format(columns))
    conn.commit()


def group_blocks():
    side = int(math.sqrt(BOARD_DIM))
    shape = (side, side)

    mat, row = [], []
    for n in range(BOARD_DIM):
        row.append(np.full(shape, n))
        if (n+1) % side == 0:
            mat.append(row)
            row = []
    return np.block(mat)


def is_filled(board):
    if np.count_nonzero(board) == BOARD_DIM**2:
        return True
    return False


def process_solution(board):
    """INSERT the generated solutions to db"""
    c = conn.cursor()
    columns = ", ".join(['"{}"'.format(n) for n in range(81)])
    c.execute("INSERT INTO solutions ({}) VALUES {};".format(
        columns, tuple(board.flatten())))
    conn.commit()
    return board


def squares():
    """
    Generates "groups" which is a dictionary
    grouping sudoku puzzle indices belonging
    to the same square. Also generates the
    reverse lookup "lookup" from index to group.
    """
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
    return COMPLETE_ROW - numbers_in_g


def construct_candidates(board, x, y):
    """
    Get eligible candidates for the cell at (x, y)
    """
    possible_from_row = COMPLETE_ROW - set(board[x, :])
    possible_from_col = COMPLETE_ROW - set(board[:, y])
    possible_from_square = choices_from_square(board, x, y)
    if DEBUG:
        print("================")
        print(board)
        print("x: ", x)
        print("y: ", y)
        print(possible_from_col & possible_from_row & possible_from_square)
    return possible_from_col & possible_from_row & possible_from_square


def get_unfilled_cell_rand(board):
    zero_indices = np.argwhere(board == 0)
    if len(zero_indices) > 0:
        cell_index = np.random.randint(len(zero_indices))
    else:
        raise IndexError("No unfilled cell remaining!")
    x, y = zero_indices[cell_index]
    return x, y


def propagate_constraint(board):
    """Fill out squares for which there is only
        one choice remaining after applying the
        previous guess"""
    x_matrix, y_matrix = np.indices((9, 9))
    for x_arr, y_arr in zip(x_matrix, y_matrix):
        for x, y in zip(x_arr, y_arr):
            candidates = construct_candidates(board, x, y)
            if len(candidates) == 1:
                board[x, y] = candidates.pop()
    return board


def backtrack_iter(board):
    stack = [board]
    while True:
        board = stack.pop()
        if is_filled(board):
            return board
        x, y = get_unfilled_cell_rand(board)
        sys.stdout.write("# filled: {}\r".format(np.count_nonzero(board)))
        sys.stdout.flush()

        candidates = construct_candidates(board, x, y)
        for candidate in candidates:
            copied = board.copy()
            copied[x, y] = candidate
            copied = propagate_constraint(copied)
            stack.append(copied)


def board_in_solutions(board, solutions):
    for sol in solutions:
        if np.all(np.equal(board, sol)):
            return True
    return False


def solution_unique(board):
    """Like backtrack_iter, but its main purpose is to
        check for uniqueness of generated puzzles from
        solutions"""
    stack, solutions = [board], []
    while True:
        try:
            board = stack.pop()
        except IndexError:
            if len(solutions) == 1:
                return True
            return False
        if is_filled(board) and not board_in_solutions(board, solutions):
            solutions.append(board)
            if len(solutions) > 1:
                return False
            continue
        x, y = get_unfilled_cell_rand(board)
        sys.stdout.write("# filled: {}\r".format(np.count_nonzero(board)))
        sys.stdout.flush()

        candidates = construct_candidates(board, x, y)
        for candidate in candidates:
            copied = board.copy()
            copied[x, y] = candidate
            copied = propagate_constraint(copied)
            stack.append(copied)


def prefill_diagonals(board):
    """
    Fill the diagonal squares (groups 0, 4, 8)
    first prior to backtracking to reduce the
    problem space.
    """
    groups, __ = squares()
    for n in (0, 4, 8):
        arr = np.arange(1, 10)
        np.random.shuffle(arr)
        for (x, y), k in zip(groups[n], arr):
            board[x, y] = k
    return board


if __name__ == "__main__":
    setup_db(conn)

    try:
        n_jobs = int(sys.argv[1])
    except (IndexError, ValueError):
        n_jobs = 1

    starting_boards = (
        prefill_diagonals(np.zeros((BOARD_DIM, BOARD_DIM,), dtype=int))
        for __ in range(n_jobs))

    with ProcessPoolExecutor() as executor:
        for result in executor.map(backtrack_iter, starting_boards):
            process_solution(result)
