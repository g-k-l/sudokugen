"""
An enhanced solver that implements
human techniques in addition to brute-force
backtracking. Give the technique used to
solve each puzzle, we can create a metric
measuring a puzzle's difficulty.

Techniques come from
http://www.sudokuoftheday.com/techniques/
"""
from collections import defaultdict, Counter
from itertools import chain, takewhile

import numpy as np

from .constants import BLOCK_ARRAY, COMPLETE_ROW
from .gen_sol import (construct_candidates, squares,
    is_filled)


def candidates_dict(puzzle):
    candidates = defaultdict(set)
    x_matrix, y_matrix = np.indices((9, 9))
    for x_arr, y_arr in zip(x_matrix, y_matrix):
        for x, y in zip(x_arr, y_arr):
            if puzzle[(x, y)] != 0:
                continue
            candidates[(x, y)] = construct_candidates(puzzle, x, y)
    return candidates


def single_candidate(puzzle, candidates):
    """
    Check whether there exists a cell that
    only has one candidate. If there exists
    such a cell, then that one candidate must
    belong to that cell.
    """
    for idx, val in candidates.iteritems():
        if len(val) == 1:
            puzzle[idx] = val
            return True
    return False


def single_position(puzzle, candidates):
    """
    Check whether there exists an element that
    only appears as a candidate once within a
    block/row/column. It means that the candidate
    must belong to that cell.
    """
    groups, __ = squares()

    blocks = groups.values()
    columns = [[(x, y) for x in range(9)] for y in range(9)]
    rows = [[(x, y) for y in range(9)] for x in range(9)]

    for indices in chain(blocks, columns, rows):
        counts = Counter(chain((candidates[index] for index in indices)))
        singles = list(filter(lambda k, v: v == 1, counts.items()))
        if singles:
            assert len(singles) == 1
            single, __ = singles[0]
            single_indices = [index for index in indices if single in candidates[index]]
            assert len(single_indices) == 1
            puzzle[single_indices[0]] = single
            return True
    return False


def candidate_line(puzzle, candidates):
    pass


def double_pair(puzzle, candidates):
    pass


def multiple_lines(puzzle, candidates):
    pass


def naked_combos(puzzle, candidates):
    pass


def hidden_combos(puzzle, candidates):
    pass


def x_wing(puzzle, candidates):
    pass


def swordfish(puzzle, candidates):
    pass


def forcing_chains(puzzle, candidates):
    pass


def nishio_search(puzzle, candidates):
    pass



TIERS = {
    single_candidate: 1,
    single_position: 1,
    candidate_line: 2,
    double_pair: 2,
    multiple_lines: 2,
    naked_combos: 3,
    hidden_combos: 3,
    x_wing: 4,
    swordfish: 4,
    nishio_search: 5
}

# in order of increasing sophistication
TECHNIQUES = [
    single_candidate,
    single_position,
    candidate_line,
    double_pair,
    multiple_lines,
    naked_combos,
    hidden_combos,
    x_wing,
    swordfish,
    nishio_search,
]


def solve(puzzle):
    history = []
    while not is_filled(puzzle):
        candidates = candidates_dict(puzzle)
        copy = puzzle.copy()
        for level, technique in enumerate(TECHNIQUES):
            success = technique(puzzle, candidates)
            history.append((copy, level))
            if success:
                break
            if level == len(TECHNIQUES) - 1:
                # too hard to be solved by human
                return history, puzzle
    # solved puzzle, with full history of steps
    return history, puzzle
