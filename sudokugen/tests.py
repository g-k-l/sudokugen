import asyncio
from io import StringIO
import logging
import time

import numpy as np
import pytest

from . import db
from . import client
from .constants import BOARD_DIM, COMPLETE_ROW, BLOCK_ARRAY
from . import gen_sol
from . import solve
from . import transform as tf


@pytest.fixture
def logfile():
    return StringIO()


@pytest.fixture
def logger(logfile):
    log = gen_sol.logger
    log.addHandler(logging.StreamHandler(logfile))
    log.setLevel(logging.DEBUG)
    return log


@pytest.fixture
def board():
    return np.array(
      [[1, 3, 5, 2, 7, 8, 9, 6, 4],
       [6, 8, 2, 4, 9, 5, 7, 1, 3],
       [9, 7, 4, 3, 1, 6, 5, 2, 8],
       [2, 6, 1, 9, 4, 7, 8, 3, 5],
       [3, 5, 7, 6, 8, 2, 4, 9, 1],
       [8, 4, 9, 1, 5, 3, 6, 7, 2],
       [7, 2, 3, 5, 6, 4, 1, 8, 9],
       [5, 9, 6, 8, 3, 1, 2, 4, 7],
       [4, 1, 8, 7, 2, 9, 3, 5, 6]], int)


@pytest.fixture
def invalid_board():
    return np.array(
      [[0, 0, 0, 0, 0, 0, 0, 0, 0],
       [0, 1, 0, 0, 0, 0, 0, 0, 0],
       [0, 2, 1, 0, 0, 0, 0, 0, 0],
       [0, 4, 0, 0, 0, 0, 0, 0, 0],
       [0, 9, 0, 0, 0, 0, 0, 0, 0],
       [0, 7, 0, 7, 0, 0, 0, 3, 0],
       [0, 5, 0, 0, 0, 0, 0, 0, 0],
       [0, 6, 0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0, 3, 0]], int)


@pytest.fixture
def corrupt_board():
    return np.array(
      [[0, 0, 0, 0, 0, 0, 0, 0, 0],
       [0, 1, 0, 0, 0, 0, 0, 0, 0],
       [0, 2, 1, 0, 0, 0, 0, 0, 0],
       [0, 4, 0, 0, -999, 0, 0, 0, 0],
       [0, 9, 0, 0, 0, 0, 0, 0, 0],
       [0, 7, 0, 100, 0, 0, 0, 3, 0],
       [0, 5, 0, 0, 0, 0, 0, 0, 0],
       [0, 6, 0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0, 3, 0]], int)


@pytest.fixture
def easy_board():
    return np.array(
      [[0, 3, 6, 8, 9, 2, 7, 1, 5],
       [5, 0, 2, 0, 7, 1, 9, 0, 3],
       [9, 0, 7, 5, 6, 3, 4, 8, 2],
       [0, 4, 3, 1, 5, 8, 2, 0, 7],
       [8, 5, 9, 6, 0, 7, 1, 3, 0],
       [7, 2, 0, 9, 3, 4, 8, 5, 6],
       [0, 0, 0, 2, 8, 6, 5, 0, 1],
       [0, 0, 0, 3, 1, 0, 0, 4, 9],
       [0, 0, 0, 7, 4, 9, 3, 2, 8]], int)


@pytest.fixture
def hard_board():
    """
    This is Skiena's example of a hard Sudoku puzzle
    (as in, difficult for a computer and impossible for
     a human to solve). See "The Algorithm Design Manual"
     Chapter 7 Section 3 for more details.
    """
    return np.array(
      [[0, 0, 0, 0, 0, 0, 0, 1, 2],
       [0, 0, 0, 0, 3, 5, 0, 0, 0],
       [0, 0, 0, 6, 0, 0, 0, 7, 0],
       [7, 0, 0, 0, 0, 0, 3, 0, 0],
       [0, 0, 0, 4, 0, 0, 8, 0, 0],
       [1, 0, 0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 1, 2, 0, 0, 0, 0],
       [0, 8, 0, 0, 0, 0, 0, 4, 0],
       [0, 5, 0, 0, 0, 0, 6, 0, 0]], int)


@pytest.fixture
def sparse_board():
    return np.array(
      [[0, 0, 0, 0, 0, 0, 0, 0, 0],
       [0, 1, 0, 0, 0, 0, 0, 0, 0],
       [0, 2, 0, 0, 0, 0, 0, 0, 0],
       [0, 4, 0, 0, 0, 0, 0, 0, 0],
       [0, 9, 0, 0, 0, 0, 0, 0, 0],
       [0, 7, 0, 0, 0, 0, 0, 3, 0],
       [0, 5, 0, 0, 0, 0, 0, 0, 0],
       [0, 6, 0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0, 0, 0]], int)


def test_squares_group():
    groups, lookup = gen_sol.squares()
    assert lookup[(1, 1)] == 0
    assert lookup[(1, 8)] == 2
    assert lookup[(8, 1)] == 6
    assert (4, 8) in groups[5]


def test_squares_choices(sparse_board):
    board = sparse_board
    choices = gen_sol.choices_from_square
    assert choices(board, 8, 1) == {1, 2, 3, 4, 7, 8, 9}
    assert choices(board, 0, 7) == {1, 2, 3, 4, 5, 6, 7, 8, 9}
    assert gen_sol.construct_candidates(board, 8, 1) == {3, 8}


def test_assert_board_is_valid(board, invalid_board, corrupt_board, easy_board, hard_board):
    assert gen_sol.assert_board_is_valid(board)
    assert gen_sol.assert_board_is_valid(easy_board)
    assert gen_sol.assert_board_is_valid(hard_board)
    assert not gen_sol.assert_board_is_valid(BLOCK_ARRAY)
    assert not gen_sol.assert_board_is_valid(invalid_board)
    assert not gen_sol.assert_board_is_valid(corrupt_board)


def test_assert_sol_is_valid(board, invalid_board, corrupt_board, easy_board, hard_board):
    assert gen_sol.assert_sol_is_valid(board)
    assert not gen_sol.assert_sol_is_valid(easy_board)
    assert not gen_sol.assert_sol_is_valid(hard_board)
    assert not gen_sol.assert_sol_is_valid(BLOCK_ARRAY)
    assert not gen_sol.assert_sol_is_valid(invalid_board)
    assert not gen_sol.assert_sol_is_valid(corrupt_board)


def test_get_unfilled_cell():
    board = np.full((BOARD_DIM, BOARD_DIM), 1)
    board[2, 2] = 0
    assert gen_sol.get_unfilled_cell_rand(board) == (2, 2)


def test_get_unfilled_cell_all_filled():
    board = np.full((BOARD_DIM, BOARD_DIM), 1)
    with pytest.raises(IndexError):
        gen_sol.get_unfilled_cell_rand(board)


def test_measure(logfile, logger):
    @gen_sol.measure(logger)
    def myfunc(a, b=2):
        time.sleep(3.2)
        return a, b
    a, b = myfunc(4)
    assert a == 4 and b == 2

    log_content = logfile.getvalue()
    assert myfunc.__name__ in log_content
    # output time will be slightly more than 3.2, but not 0.1 more
    assert "3.2" in log_content


def test_backtrack_iter_basic(easy_board):
    # use a partially solved board so that the tests
    # do not run for too long.
    sol = gen_sol.backtrack_iter(easy_board)
    assert len(np.argwhere(sol == 0)) == 0
    gen_sol.assert_sol_is_valid(sol)


# def test_backtrack_iter(hard_board):
#     sol = gen_sol.backtrack_iter(hard_board)
#     assert len(np.argwhere(sol == 0)) == 0
#     gen_sol.assert_sol_is_valid(sol)


# def test_from_empty_board():
#     sol = gen_sol.from_empty_board()
#     assert len(np.argwhere(sol == 0)) == 0
#     gen_sol.assert_sol_is_valid(sol)


def test_x_translate(board):
    assert np.all(np.equal(tf.x_translate(board, times=3), board))
    for n in range(3):
        gen_sol.assert_sol_is_valid(tf.x_translate(board, times=n+1))


def test_y_translate(board):
    assert np.all(np.equal(tf.y_translate(board, times=3), board))
    for n in range(3):
        gen_sol.assert_sol_is_valid(tf.y_translate(board, times=n+1))


def test_rotate(board):
    for n in range(3):
        gen_sol.assert_sol_is_valid(tf.rotate(board, times=n+1))


def test_mirror_x(board):
    gen_sol.assert_sol_is_valid(tf.mirror_x(board))


def test_mirror_y(board):
    gen_sol.assert_sol_is_valid(tf.mirror_y(board))


def test_shuff_numbers(board):
    gen_sol.assert_sol_is_valid(tf.shuffle_numbers(board))


def test_candidates_dict(board):
    index1, index2 = (2, 1), (3, 1)
    orig_val1, orig_val2 = board[index1], board[index2]
    board[index1] = 0
    board[index2] = 0
    candidates = dict(solve.candidates_dict(board))
    assert index1 in candidates and index2 in candidates
    assert (4, 1) not in candidates
    assert candidates[index1] == {orig_val1}
    assert candidates[index2] == {orig_val2}


def test_remove_candidates_from_line():
    candidates = {
        (1, 1): {1, 2, 4, 3},
        (1, 2): {3, 4, 5},
        (1, 8): {2, 4, 5},
    }
    lineno, n = 1, 4
    expected = {
        (1, 1): {1, 2, 4, 3},
        (1, 2): {3, 5},
        (1, 8): {2, 5},
    }
    solve.remove_candidates_from_line(candidates, n, lineno, except_for=[(1,1)])
    assert candidates == expected


def test_related_blocks():
    assert len(solve.related_blocks()) == 18


def test_lines_in_block_pair():
    block_pairs = [(0, 2), (1, 7), (2, 3)]
    expected_linenos = [[0, 1, 2], [12, 13, 14], []]
    for blocks, expected in zip(block_pairs, expected_linenos):
        assert solve.lines_in_block_pair(*blocks) == expected
