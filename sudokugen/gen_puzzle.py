
import math
from concurrent.futures import ProcessPoolExecutor
import sqlite3
import sys

import numpy as np

from .constants import BOARD_DIM
from .gen_sol import solution_unique


def to_db(board):
    """INSERT the generated puzzle to db"""
    c = conn.cursor()
    columns = ", ".join(['"{}"'.format(n) for n in range(81)])
    c.execute("INSERT INTO puzzles ({}) VALUES {};".format(
        columns, tuple(board.flatten())))
    conn.commit()
    return board


def create_puzzle(board):
    positions = np.arange(81)
    np.random.shuffle(positions)
    positions = list(positions)

    while True:
        if not positions:
            return board

        position = positions.pop()
        x = position % BOARD_DIM
        y = math.floor(position / BOARD_DIM)

        old_val = board[x, y]
        board[x, y] = 0
        if not solution_unique(board):
            board[x, y] = old_val


if __name__ == "__main__":
    setup_db(conn)
    try:
        n_jobs = int(sys.argv[1])
    except (IndexError, ValueError):
        n_jobs = 1

    starting_boards = from_db(conn, limit=n_jobs)
    with ProcessPoolExecutor() as executor:
        for result in executor.map(create_puzzle, starting_boards):
            print(to_db(result))
