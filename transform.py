"""
Defines transformation which would create
perceptually different puzzles from each
existing puzzle.
"""
import numpy as np

from constants import BOARD_DIM


def x_translate(board, times=1):
    return np.roll(board, shift=times*3, axis=0)


def y_translate(board, times=1):
    return np.roll(board, shift=times*3, axis=1)


def rotate(board, times=1):
    return np.rot90(board, k=times)


def mirror_x(board):
    return np.flipud(board)


def mirror_y(board):
    return np.fliplr(board)


def mirror_major_diagonal(board):
    raise NotImplementedError("Equivalent to rotate + mirror.")


def mirror_minor_diagonal(board):
    raise NotImplementedError("Equivalent to rotate + mirror.")


def shuffle_numbers(board):
    """
    Produce one of 9!-1 (362879) equivalent
    puzzles from the original by mapping
    each number to a different number.
    """
    num_map = np.arange(BOARD_DIM)
    np.random.shuffle(np.arange(BOARD_DIM))
    copy = -board
    for i, n in enumerate(num_map):
        copy[copy == -(i+1)] = n + 1
    return copy
