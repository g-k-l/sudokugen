"""
This file contains a backtracking
sudoku solver.

Reference implementation by Peter Norvig:
the DFS/backtracking solver:
http://norvig.com/sudoku.html
"""

from collections import defaultdict
from copy import deepcopy

EMPTY = 0
DIM = 9
SIZE = 81


def empty_puzzle():
    """Returns an tuple of 81 zeros"""
    return [EMPTY for __ in range(SIZE)]


def block(k):
    r, c = (k // DIM), (k % DIM)
    return (r // 3) + 3*(c // 3)


def block_indices():
    blocks = defaultdict(set)
    for k in range(SIZE):
        r, c = (k // DIM), (k % DIM)
        b = (r // 3) + 3*(c // 3)
        blocks[b].add(k)
    # remove the default property
    return dict(blocks)


def indices():
    rows = defaultdict(set)
    cols = defaultdict(set)
    for k in range(SIZE):
        rows[k // DIM].add(k)
        cols[k % DIM].add(k)
    # remove the default property
    return dict(rows), dict(cols)


ROW_INDICES, COL_INDICES = indices()
BLOCK_INDICES = block_indices()

COMPLETE_ROW = {n+1 for n in range(DIM)}

# "k" is the unique label for a cell, a number from 0 to 80
# A cell can belong to three units: the row, column, and block unit.
UNITS_OF = {
    k: [ROW_INDICES[k // DIM], COL_INDICES[k % DIM], BLOCK_INDICES[block(k)]]
    for k in range(SIZE)
}
# A cell's peers consists of the set of all cells in its row, column, and block.
PEERS_OF = {
    k: (ROW_INDICES[k // DIM] | COL_INDICES[k % DIM] | BLOCK_INDICES[block(k)]) - {k}
    for k in range(SIZE)
}


class SudokuBaseException(Exception):
    pass


class NoSolution(SudokuBaseException):
    pass


def assign(cands_of, k, val):
    """Assign val to k by eliminating
        all other_vals in cands_of[k]"""
    for other_val in COMPLETE_ROW:
        if other_val == val:
            continue
        eliminate(cands_of, k, other_val)
    return cands_of


def eliminate(cands_of, k, val):
    """
    Eliminate val from cands_of[k]

    (1) If a square has only one possible value,
        then eliminate that value from the square's peers.
    (2) If a unit has only one possible place for a value,
        then put the value there.
    """
    if val not in cands_of[k]:
        return cands_of

    cands_of[k].remove(val)
    if len(cands_of[k]) == 0:
        raise NoSolution("contradiction")
    elif len(cands_of[k]) == 1:
        (val2,) = cands_of[k]
        for p in PEERS_OF[k]:
            eliminate(cands_of, p, val2)
        return cands_of

    for unit in UNITS_OF[k]:
        # location in unit where val is possible
        locs = [l for l in unit if val in cands_of[l]]
        if len(locs) == 0:
            raise NoSolution("contradiction")
        elif len(locs) == 1:
            (loc,) = locs
            assign(cands_of, loc, val)
            return cands_of


def init_cands_of(puzzle):
    cands_of = {k: set(COMPLETE_ROW) for k in range(SIZE)}
    for k, val in enumerate(puzzle):
        if val == EMPTY:
            continue
        assign(cands_of, k, val)

    return cands_of


def is_solved(cands_of):
    for vals in cands_of.values():
        if len(vals) > 1:
            return False
    return True


def solve(puzzle):
    stack = [init_cands_of(puzzle)]
    while stack:
        cands_of = stack.pop()

        if is_solved(cands_of):
            return cands_of

        by_constraint = [(k, cands) for k, cands in
            sorted(cands_of.items(), key=lambda item: len(item[1]), reverse=True)]

        for k, cands in by_constraint:
            for val in cands:
                next_cands_of = deepcopy(cands_of)
                assign(next_cands_of, k, val)
                stack.append(next_cands_of)
    raise NoSolution("contradiction")

