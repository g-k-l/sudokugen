"""
Create puzzles by:
    - randomly assigning some values to start
    - Attempt to solve the generated puzzle
    - if a solution is found, return both the
      puzzle and the solution
"""
from copy import deepcopy
from enum import Enum
import random

from .solver import (empty_puzzle, init_cands_of, assign, dfs,
                     maybe_conv_inv, maybe_conv, SudokuBaseException,
                     NoSolution, SIZE, DIM)


class Difficulty(Enum):
    EASY = 30
    MEDIUM = 24
    HARD = 17
    MANY_SOLS = 14


class MaxRetriesExceeded(SudokuBaseException):
    pass


def cands_to_puzzle(cands_of):
    cands_of = deepcopy(cands_of)
    return [0 if len(cands_of[k]) != 1 else cands_of[k].pop() for k in range(SIZE)]


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
                uncertain_cells = [k for k in cands_of.keys() if len(cands_of[k]) > 1]
                if uncertain_cells:
                    rand_cell = random.choice(uncertain_cells)
                    rand_val = random.choice(list(cands_of[rand_cell]))
                    assign(cands_of, rand_cell, rand_val)
                else:
                    break
        except NoSolution:
            continue
        else:
            try:
                puzzle = cands_to_puzzle(cands_of)
                # having generated a puzzle by randomly assigning cell values
                # find the full solution via DFS
                solution = dfs(cands_of)
            except NoSolution:
                continue
            else:
                return puzzle, maybe_conv_inv(solution)
    raise MaxRetriesExceeded(
        "Attempted %s times to generate puzzle with %s"
        % (max_retries, difficulty))


"""
The following functions allow us to generate
perceptually different puzzles from existing
puzzles via transformations such as rotation
and shuffling value labels.
"""

def row_translate(puzzle, times=1):
    puzzle = maybe_conv(puzzle)
    for __ in range(times):
        puzzle = puzzle[27:] + puzzle[:27]
    return maybe_conv_inv(puzzle)


def col_translate(puzzle, times=1):
    for __ in range(times):
        for row_num in len(DIM):
            puzzle[row_num] = puzzle[row_num][3:] + puzzle[row_num][:3]
    return puzzle


def shuffle_numbers(puzzle):
    """
    Produce one of 9!-1 (362879) equivalent
    puzzles from the original by mapping
    each number to a different number.
    """
    num_map = dict(zip(range(1, 10), random.shuffle(range(1,10))))
    for k in range(len(SIZE)):
        if puzzle[k] == 0:
            continue
        puzzle[k] = num_map[puzzle[k]]
    return puzzle

