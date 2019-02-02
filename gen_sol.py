
from concurrent.futures import ProcessPoolExecutor
import math
import sqlite3

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


def is_a_solution(board):
    for n in range(BOARD_DIM):
        row_ok = set(board[n, :]) == COMPLETE_ROW
        col_ok = set(board[:, n]) == COMPLETE_ROW
        if not (row_ok and col_ok):
            return False
    return True


def process_solution(bc):
    c = conn.cursor()
    c.execute("INSERT INTO solutions VALUES {};".format(
        tuple(bc.board.flatten())))
    conn.commit()
    bc.finished = True
    return bc


def construct_candidates(board, x, y):
    possible_from_col = COMPLETE_ROW - set(board[:, y])
    possible_from_row = COMPLETE_ROW - set(board[x, :])
    return possible_from_col & possible_from_row


def backtrack(bc, positions):
    board = bc.board
    print(positions)

    if is_a_solution(board):
        return process_solution(bc)

    x = positions[0] % BOARD_DIM
    y = math.floor(positions[0] / BOARD_DIM)

    candidates = construct_candidates(board, x, y)

    for candidate in candidates:
        board[x, y] = candidate
        backtrack(bc, positions[0:])
        if bc.finished:
            return bc
        board[x, y] = REP_UNFILLED_SQUARE


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
    initial_data = zip(starting_boards, positions_remainings)

    print(backtrack(starting_boards[0], positions_remainings[0]))

    # with ProcessPoolExecutor(max_workers=n_workers) as executor:
    #     for bc in zip(initial_data, executor.map(backtrack, initial_data)):
    #         # TODO: anything important to do here?
    #         print(bc)
