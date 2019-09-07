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
    """Given a cell label (0-80), return
    the 3x3 block for which it is in.

    >>> block(3)
    1
    >>> block(72)
    6
    """
    r, c = (k // DIM), (k % DIM)
    return 3*(r // 3) + (c // 3)


def block_indices():
    """
    Returns a dict where keys are block labels
    (int from 0-8) and vals are the cell labels
    that belong to the block.

    >>> indices = block_indices()[0]
    >>> indices == {0, 1, 2, 9, 10, 11, 18, 19, 20}
    True
    >>> indices = block_indices()[4]
    >>> indices == {30, 31, 32, 39, 40, 41, 48, 49, 50}
    True
    """
    blocks = defaultdict(set)
    for k in range(SIZE):
        r, c = (k // DIM), (k % DIM)
        b = block(k)
        blocks[b].add(k)
    # remove the default property
    return dict(blocks)


def indices():
    """
    Returns two dicts, where the keys are
    row/col labels and the vals are cell labels
    which belong to the corresponding row/col.

    >>> rows, cols = indices()
    >>> rows[0] == {0, 1, 2, 3, 4, 5, 6, 7, 8}
    True
    >>> rows[4] == {36, 37, 38, 39, 40, 41, 42, 43, 44}
    True
    >>> cols[2] == {2, 11, 20, 29, 38, 47, 56, 65, 74}
    True
    >>> cols[9]
    Traceback (most recent call last):
    ...
    KeyError: 9
    """
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
    """
    Assign val to k by eliminating all other_vals in cands_of[k]

    >>> cands_of = {k: set(COMPLETE_ROW) for k in range(SIZE)}
    >>> assign(cands_of, 0, 1)
    >>> cands_of[0] == {1}
    True
    >>> cands_of[10] == {2, 3, 4, 5, 6, 7, 8, 9} # same block
    True
    >>> cands_of[8] == {2, 3, 4, 5, 6, 7, 8, 9} # same col
    True
    >>> cands_of[1] == {2, 3, 4, 5, 6, 7, 8, 9} # same row
    True
    """
    for other_val in COMPLETE_ROW:
        if other_val == val:
            continue
        eliminate(cands_of, k, other_val)


def eliminate(cands_of, k, val):
    """
    Eliminate val from cands_of[k]

    (1) If a square has only one possible value,
        then eliminate that value from the square's peers.
    (2) If a unit has only one possible place for a value,
        then put the value there.

    :cands_of: dict. keys are cell labels (int) and
        vals are sets of ints, representing possible
        values for the cell.
    :k: the cell label (int)
    :val: the val to eliminate from cands_of[k] (int)

    # trivial example:
    >>> cands_of = {k: set(COMPLETE_ROW) for k in range(SIZE)}
    >>> eliminate(cands_of, 0, 1)
    >>> cands_of[0] == {2, 3, 4, 5, 6, 7, 8, 9}
    True
    """
    if val not in cands_of[k]:
        return

    cands_of[k].remove(val)
    if len(cands_of[k]) == 0:
        raise NoSolution("contradiction")
    elif len(cands_of[k]) == 1:
        (val2,) = cands_of[k]
        for p in PEERS_OF[k]:
            eliminate(cands_of, p, val2)
        return

    for unit in UNITS_OF[k]:
        # location in unit where val is possible
        locs = [l for l in unit if val in cands_of[l]]
        if len(locs) == 0:
            raise NoSolution("contradiction")
        elif len(locs) == 1:
            (loc,) = locs
            assign(cands_of, loc, val)
            return


def init_cands_of(puzzle):
    """
    Given the puzzle's state, create its candidate
    dict by assigning cells which already have values.

    For a puzzle having unique solution, a single application
    of this function (usually) leads to a complete solution.

    :puzzle: a list of ints, each of which is from 0 to 9

    >>> puzzle = []
    """
    cands_of = {k: set(COMPLETE_ROW) for k in range(SIZE)}
    for k, val in enumerate(puzzle):
        if val == EMPTY:
            continue
        assign(cands_of, k, val)

    return cands_of


def is_solved(cands_of):
    """A puzzle is solved if its candidate
        dict has only one candidate for each cell"""
    for vals in cands_of.values():
        if len(vals) > 1:
            return False
    return True


def solve(puzzle):
    """For puzzles which are not known to have unique
    solutions, use this function, which implements
    DFS-backtracking, searching solutions by guessing
    values in most-constrained cells first."""
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
                try:
                    assign(next_cands_of, k, val)
                except NoSolution:
                    # the value leads to a dead-end,
                    # do not append it to the stack
                    continue
                else:
                    stack.append(next_cands_of)
    raise NoSolution("contradiction")

if __name__ == "__main__":
    import doctest
    doctest.testmod()