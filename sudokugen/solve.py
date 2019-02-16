"""
An enhanced solver that implements
human techniques in addition to brute-force
backtracking. Given the technique used to
solve each puzzle, we can create a metric
measuring a puzzle's difficulty.

Techniques come from
http://www.sudokuoftheday.com/techniques/
"""
from collections import defaultdict, Counter
from functools import lru_cache
from itertools import chain, takewhile, islice, combinations

import numpy as np

from .constants import BLOCK_ARRAY, COMPLETE_ROW
from .gen_sol import (construct_candidates, squares,
    is_filled)


def candidates_dict(puzzle):
    """
    Construct the "Pencil Marks" for puzzle.
    """
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


def move(puzzle, candidates):
    return single_candidate(puzzle, candidates) or single_position(puzzle, candidates)


@lru_cache()
def _line(lineno):
    """
    Get the indices of a line labeled lineno.
    Labeling works as follows:
        0: x=0,
        1: x=1,
        ...
        8: x=8,
        9: y=0,
        10: y=1,
        ...
        17: y=8
    """
    if 0 < lineno < 8:
        return [(lineno, n) for n in range(9)]
    elif 9 < lineno < 18:
        return [(n, lineno - 9) for n in range(9)]
    else:
        raise IndexError("Only 18 possible lines!")


def candidates_for_n_in_g(candidates, n, g):
    """
    Get all indices for which n appears a candidate
    in block g.
    """
    groups, __ = squares()
    block = groups[g]

    cand_indices = []
    for x, y in block:
        if n in candidates[(x, y)]:
            cand_indices.append((x, y))
    return cand_indices


def remove_candidates_from_line(candidates, n, lineno, except_for=None):
    """
    Remove all candidates of the number n in
    the line labeled lineno
    """
    if except_for is None:
        except_for = []
    for x, y in _line(lineno):
        if (x, y) in except_for or (x, y) not in candidates:
            continue
        candidates[(x, y)].discard(n)


def candidate_line(candidates):
    """
    For each block, check whether there is a number
    that only appears in a single line as a candidate.
    For each such number, eliminate the pencil mark of
    that number in the other two blocks on that line.

    Stop after finding one such number and having processed
    that number for each block.
    """
    num_order, group_order = np.arange(9), np.arange(9)
    np.random.shuffle(group_order)
    np.random.shuffle(num_order)

    sentinel = False
    for n in num_order:
        if sentinel:
            return
        for g in group_order:
            cands = candidates_for_n_in_g(candidates, n, g)
            x_indices = [c[0] for c in cands]
            y_indices = [c[1] for c in cands]
            if len(x_indices) == 1:
                lineno = x_indices[0]
                candidates = remove_candidates_from_line(candidates, n, lineno, cands)
                sentinel = True 
            elif len(y_indices) == 1:
                lineno = y_indices[0] + 9
                candidates = remove_candidates_from_line(candidates, n, lineno, cands) 
                sentinel = True 


def blocks_in_line():
    return [(0, 1, 2), (3, 4, 5), (6, 7, 8),
        (0, 3, 6), (1, 4, 7), (2, 5, 8)]


@lru_cache()
def related_blocks():
    return list(chain(*[combinations(blocks, 2) for blocks in blocks_in_line()]))


def lines_in_block_pair(block1, block2):
    """Return lines which connect the two blocks"""
    groups, __ = squares()
    block1_indices, block2_indices = groups[block1], groups[block2]
    xs_in_block1, ys_in_block1 = zip(*block1_indices)
    xs_in_block2, ys_in_block2 = zip(*block2_indices)

    linenos = []
    for x in set(xs_in_block1) & set(xs_in_block2):
        linenos.append(x)
    for y in set(ys_in_block1) & set(ys_in_block2):
        linenos.append(y+9)    
    return linenos


def find_double_pair_in(block1, block2):

    groups, __ = square()

    block1_indices, block2_indices = groups[block1], groups[block2]

     


def double_pair(puzzle, candidates):
    """
    For each pair of related blocks, check whether
    there exists a number that only appears in two
    same lines in those blocks. Remove that number
    from the third line in the third related block.

    Stop after finding on such number and having
    processed that number for the third related block.
    """
    num_order = np.arange(9)
    np.random.shuffle(num_order)

    block_pairs = related_blocks()

    for n in num_order:
        for block_pair in block_pairs:
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


MOVES = [single_candidate, single_position]

REDUCTIONS = [
    candidate_line,
    double_pair,
    multiple_lines,
    naked_combos,
    hidden_combos,
    x_wing,
    swordfish,
    nishio_search, 
]

TIERS = {
    candidate_line: 2,
    double_pair: 2,
    multiple_lines: 2,
    naked_combos: 3,
    hidden_combos: 3,
    x_wing: 4,
    swordfish: 4,
    nishio_search: 5
}


def solve(puzzle):
    history = []
    while not is_filled(puzzle):
        candidates = candidates_dict(puzzle)
        copy = puzzle.copy()

        # modifies puzzle
        success = move(puzzle, candidates)
        if success:
            history.append((copy, move))
            continue 
        else:
            stuck = True
            for reduction in enumerate(REDUCTIONS):
                reduction(candidates) # modifies candidates
                history.append((copy, reduction))
                success = move(puzzle, candidates)
                if success:
                    stuck = False
                    break
            if stuck:
                # too hard to be solved by human
                return history, puzzle

    # solved puzzle, with full history of steps
    return history, puzzle
