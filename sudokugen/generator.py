"""
Create puzzles by:
    - randomly assigning 17 values to start
    - Attempt to solve the generated puzzle
    - if a solution is found, return both the
      puzzle and the solution
"""
from enum import Enum
import random

from .solver import (empty_puzzle, init_cands_of, assign, dfs,
                     maybe_conv_inv, SudokuBaseException, NoSolution)


class Difficulty(Enum):
    EASY = 31
    MEDIUM = 24
    HARD = 17
    MANY_SOLS = 14


class MaxRetriesExceeded(SudokuBaseException):
    pass


def generate(difficulty=Difficulty.MEDIUM, max_retries=10):
    """
    Generate a puzzle with specified difficulty,
    measured by the number of filled starting cells.

    Note, 17 filled cells is a necessary condition
    for a unique solution (whether it's sufficient is
    not as clear). But we can still find a solution
    via DFS when there are fewer than 17.
    """
    for __ in range(max_retries):
        puzzle = empty_puzzle()
        cands_of = init_cands_of(puzzle)
        try:
            # randomly assign cell values based on difficulty
            for __ in range(difficulty.value):
                rand_cell = random.choice(
                    [k for k in cands_of.keys() if len(cands_of[k]) > 1])
                rand_val = random.choice(list(cands_of[rand_cell]))
                assign(cands_of, rand_cell, rand_val)
        except NoSolution:
            continue
        else:
            try:
                # having generated a puzzle by randomly assigning cell values
                # find the full solution via DFS
                solution = dfs(cands_of)
            except NoSolution:
                continue
            else:
                return maybe_conv_inv(solution)
    raise MaxRetriesExceeded(
        "Attempted %s times to generate puzzle with %s"
        % (max_retries, difficulty))
