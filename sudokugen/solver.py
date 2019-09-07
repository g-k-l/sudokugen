"""
This file contains a backtracking
sudoku solver.

Reference implementation by Peter Norvig:
the DFS/backtracking solver:
http://norvig.com/sudoku.html
"""

from collections import defaultdict
from copy import deepcopy
from itertools import chain


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


class InvalidPuzzle(SudokuBaseException):
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

    >>> puzzle = empty_puzzle()
    >>> puzzle[3] = 1; puzzle[4] = 2
    >>> cands_of = init_cands_of(puzzle)
    >>> cands_of[3] == {1}
    True
    >>> cands_of[4] == {2}
    True
    >>> cands_of[5] == {3, 4, 5, 6, 7, 8, 9} # same block as cells 3 and 4
    True
    >>> cands_of[31] == {1, 3, 4, 5, 6, 7, 8, 9} # same col as cell 4
    True
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


def is_valid(puzzle):
    """Ensures that each cell can only contain
    an integer from 0 to 9."""
    for val in maybe_conv(puzzle):
        if val not in list(range(10)):
            return False
    return True


def maybe_conv(l):
    """
    Flattens l if l is a list or a tuple.

    >>> l = [[1, 2, 3], [4, 5, 6]]
    >>> maybe_conv(l)
    [1, 2, 3, 4, 5, 6]

    >>> l = [1, 2, 3, 4]
    >>> maybe_conv(l)
    [1, 2, 3, 4]
    """
    if isinstance(l[0], list) or isinstance(l[0], tuple):
        return list(chain(*l))
    return l


def maybe_conv_inv(l):
    """
    Converts a list of ints to a list of list, each
    having 9 elements.

    >>> l = [1, 2, 3, 4, 5, 6, 7, 8, 9]*9
    >>> conv_l = maybe_conv_inv(l)
    >>> conv_l == [[1, 2, 3, 4, 5, 6, 7, 8, 9] for __ in range(9)]
    True
    """
    if isinstance(l[0], list) or isinstance(l[0], tuple):
        return l
    ret = []
    for k in range(len(l)):
        if (k // DIM) >= len(ret):
            ret.append([])
        ret[k // DIM].append(l[k])
    return ret


def dfs(cands_of):
    """
    Search for solutions via DFS-backtracking by guessing
    values in the most-constrained cells first.

    :cands_of: dict of sets, which map cell labels to candidates
    """
    stack = [cands_of]
    while stack:
        cands_of = stack.pop()

        if is_solved(cands_of):
            return [cands_of[k].pop() for k in range(SIZE)]

        by_constraint = [(k, cands) for k, cands in
                         sorted(cands_of.items(), key=lambda item: len(item[1]), reverse=True)]

        for k, cands in by_constraint:
            if len(cands) == 1:
                continue
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


def solve(given):
    """
    Solve the given puzzle. If the puzzle has no solution,
    then raise NoSolution(...).

    >>> puzzle = [[0, 3, 6, 8, 9, 2, 7, 1, 5],
    ...           [5, 0, 2, 0, 7, 1, 9, 0, 3],
    ...           [9, 0, 7, 5, 6, 3, 4, 8, 2],
    ...           [0, 4, 3, 1, 5, 8, 2, 0, 7],
    ...           [8, 5, 9, 6, 0, 7, 1, 3, 0],
    ...           [7, 2, 0, 9, 3, 4, 8, 5, 6],
    ...           [0, 0, 0, 2, 8, 6, 5, 0, 1],
    ...           [0, 0, 0, 3, 1, 0, 0, 4, 9],
    ...           [0, 0, 0, 7, 4, 9, 3, 2, 8]]

    >>> solution = solve(puzzle)
    >>> solution == [[4, 3, 6, 8, 9, 2, 7, 1, 5],
    ...              [5, 8, 2, 4, 7, 1, 9, 6, 3],
    ...              [9, 1, 7, 5, 6, 3, 4, 8, 2],
    ...              [6, 4, 3, 1, 5, 8, 2, 9, 7],
    ...              [8, 5, 9, 6, 2, 7, 1, 3, 4],
    ...              [7, 2, 1, 9, 3, 4, 8, 5, 6],
    ...              [3, 9, 4, 2, 8, 6, 5, 7, 1],
    ...              [2, 7, 8, 3, 1, 5, 6, 4, 9],
    ...              [1, 6, 5, 7, 4, 9, 3, 2, 8]]
    True

    Typically, for a puzzle having unique solution,
    the puzzle is solved in the first step of the
    search.

    For puzzles which are not known to have unique
    solutions, search for solutions via DFS-backtracking
    by guessing values in the most-constrained cells first.
    """
    if not is_valid(given):
        raise InvalidPuzzle("Each cell must contain numbers from 0 to 9")

    puzzle = maybe_conv(given)
    solution = dfs(init_cands_of(puzzle))
    if puzzle != given:
        return maybe_conv_inv(solution)
    return solution


if __name__ == "__main__":
    import doctest
    doctest.testmod()
