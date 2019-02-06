
import numpy as np
import pytest

import gen_sol
import transform


def test_squares_group():
    groups, lookup = gen_sol.squares()
    assert lookup[(1, 1)] == 0
    assert lookup[(1, 8)] == 6
    assert lookup[(8, 1)] == 2
    assert (4, 8) in groups[7]


def test_squares_choices():
    board = np.array(
      [[0, 0, 0, 0, 0, 0, 0, 0, 0],
       [0, 1, 0, 0, 0, 0, 0, 0, 0],
       [0, 2, 0, 0, 0, 0, 0, 0, 0],
       [0, 4, 0, 0, 0, 0, 0, 0, 0],
       [0, 9, 0, 0, 0, 0, 0, 0, 0],
       [0, 7, 0, 0, 0, 0, 0, 3, 0],
       [0, 5, 0, 0, 0, 0, 0, 0, 0],
       [0, 6, 0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0, 0, 0]])

    choices = gen_sol.choices_from_square
    assert choices(board, 8, 1) == {1, 2, 3, 4, 7, 8, 9}
    assert choices(board, 0, 7) == {1, 2, 3, 4, 5, 6, 7, 8, 9}
    assert gen_sol.construct_candidates(board, 8, 1) == {3, 8}


def test_get_unfilled_cell():
    board = np.array(
      [[1, 1, 1, 1, 1, 1, 1, 1, 1],
       [1, 1, 1, 1, 1, 1, 1, 1, 1],
       [1, 1, 0, 1, 1, 1, 1, 1, 1],
       [1, 1, 1, 1, 1, 1, 1, 1, 1],
       [1, 1, 1, 1, 1, 1, 1, 1, 1],
       [1, 1, 1, 1, 1, 1, 1, 1, 1],
       [1, 1, 1, 1, 1, 1, 1, 1, 1],
       [1, 1, 1, 1, 1, 1, 1, 1, 1],
       [1, 1, 1, 1, 1, 1, 1, 1, 1]])
    assert gen_sol.get_unfilled_cell_rand(board) == (2, 2)


def test_get_unfilled_cell_all_filled():
    board = np.array(
      [[1, 1, 1, 1, 1, 1, 1, 1, 1],
       [1, 1, 1, 1, 1, 1, 1, 1, 1],
       [1, 1, 1, 1, 1, 1, 1, 1, 1],
       [1, 1, 1, 1, 1, 1, 1, 1, 1],
       [1, 1, 1, 1, 1, 1, 1, 1, 1],
       [1, 1, 1, 1, 1, 1, 1, 1, 1],
       [1, 1, 1, 1, 1, 1, 1, 1, 1],
       [1, 1, 1, 1, 1, 1, 1, 1, 1],
       [1, 1, 1, 1, 1, 1, 1, 1, 1]])
    with pytest.raises(IndexError):
        gen_sol.get_unfilled_cell_rand(board)


def test_x_translate():
    pass


def test_y_translate():
    pass


def test_rotate():
    pass


def test_mirror():
    pass


def test_shuff_numbers():
    pass
