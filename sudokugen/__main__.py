import sys
import numpy as np
from .client import client
from .db import setup_db
from .gen_sol import (main, backtrack_iter, create_puzzle_from_board,
    starting_board)

if __name__ == "__main__":
    try:
        sys.argv[1]
    except IndexError:
        print('Valid options are "play", "solve", "gen" and "genmany"')
        sys.exit(0)

    if sys.argv[1] == "play":
        sys.exit(client() or 0)     
    elif sys.argv[1] == "solve":
        board = np.array([int(c) for c in sys.argv[2]]).reshape(9, 9)
        solution = backtrack_iter(board)
        print(solution)
        sys.exit(0)
    elif sys.argv[1] == "gen":
        board = starting_board()
        puzzle = create_puzzle_from_board(backtrack_iter(board))
        print(puzzle)
        sys.exit(0)
    elif sys.argv[1] == "genmany":
        setup_db()
        try:
            n_jobs = int(sys.argv[1])
        except (IndexError, ValueError):
            n_jobs = None 
        sys.exit(main(n_jobs) or 0)
    else:
        print('Valid options are "play", "solve", "gen" and "genmany"')
        sys.exit(0)
