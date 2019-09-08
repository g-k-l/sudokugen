import doctest
from unittest import TestCase


from . import solver
from . import generator as g
from .generator import Difficulty, MaxRetriesExceeded


def load_tests(loader, tests, ignore):
    """Allows unittest to run doctests"""
    tests.addTests(doctest.DocTestSuite(solver))
    return tests


class TestSolve(TestCase):
    def test_easy_board(self):
        l = [[0, 3, 6, 8, 9, 2, 7, 1, 5],
             [5, 0, 2, 0, 7, 1, 9, 0, 3],
             [9, 0, 7, 5, 6, 3, 4, 8, 2],
             [0, 4, 3, 1, 5, 8, 2, 0, 7],
             [8, 5, 9, 6, 0, 7, 1, 3, 0],
             [7, 2, 0, 9, 3, 4, 8, 5, 6],
             [0, 0, 0, 2, 8, 6, 5, 0, 1],
             [0, 0, 0, 3, 1, 0, 0, 4, 9],
             [0, 0, 0, 7, 4, 9, 3, 2, 8]]

        expected = [[4, 3, 6, 8, 9, 2, 7, 1, 5],
                    [5, 8, 2, 4, 7, 1, 9, 6, 3],
                    [9, 1, 7, 5, 6, 3, 4, 8, 2],
                    [6, 4, 3, 1, 5, 8, 2, 9, 7],
                    [8, 5, 9, 6, 2, 7, 1, 3, 4],
                    [7, 2, 1, 9, 3, 4, 8, 5, 6],
                    [3, 9, 4, 2, 8, 6, 5, 7, 1],
                    [2, 7, 8, 3, 1, 5, 6, 4, 9],
                    [1, 6, 5, 7, 4, 9, 3, 2, 8]]
        self.assertEqual(solver.solve(l), expected)

    def test_solve_hard_board(self):
        """
        This is Skiena's example of a hard Sudoku puzzle.
        See "The Algorithm Design Manual" Chapter 7 Section 3
        for more details.
        """
        l = [[0, 0, 0, 0, 0, 0, 0, 1, 2],
             [0, 0, 0, 0, 3, 5, 0, 0, 0],
             [0, 0, 0, 6, 0, 0, 0, 7, 0],
             [7, 0, 0, 0, 0, 0, 3, 0, 0],
             [0, 0, 0, 4, 0, 0, 8, 0, 0],
             [1, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 1, 2, 0, 0, 0, 0],
             [0, 8, 0, 0, 0, 0, 0, 4, 0],
             [0, 5, 0, 0, 0, 0, 6, 0, 0]]
        sol = solver.solve(l)
        self.assertTrue(solver.is_valid(sol), sol)

    def test_invalid_board(self):
        l = [[0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 1, 0, 0, 0, 0, 0, 0, 0],
             [0, 2, 1, 0, 0, 0, 0, 0, 0],
             [0, 4, 0, 0, 0, 0, 0, 0, 0],
             [0, 9, 0, 0, 0, 0, 0, 0, 0],
             [0, 7, 0, 7, 0, 0, 0, 3, 0],
             [0, 5, 0, 0, 0, 0, 0, 0, 0],
             [0, 6, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 3, 0]]

        with self.assertRaises(solver.NoSolution):
            solver.solve(l)

    def test_finished_board(self):
        l = [[1, 3, 5, 2, 7, 8, 9, 6, 4],
             [6, 8, 2, 4, 9, 5, 7, 1, 3],
             [9, 7, 4, 3, 1, 6, 5, 2, 8],
             [2, 6, 1, 9, 4, 7, 8, 3, 5],
             [3, 5, 7, 6, 8, 2, 4, 9, 1],
             [8, 4, 9, 1, 5, 3, 6, 7, 2],
             [7, 2, 3, 5, 6, 4, 1, 8, 9],
             [5, 9, 6, 8, 3, 1, 2, 4, 7],
             [4, 1, 8, 7, 2, 9, 3, 5, 6]]
        sol = solver.solve(l)
        self.assertEqual(l, sol, sol)

    def test_corrupt_board(self):
        l = [[0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 1, 0, 0, 0, 0, 0, 0, 0],
             [0, 2, 1, 0, 0, 0, 0, 0, 0],
             [0, 4, 0, 0, -999, 0, 0, 0, 0],
             [0, 9, 0, 0, 0, 0, 0, 0, 0],
             [0, 7, 0, 100, 0, 0, 0, 3, 0],
             [0, 5, 0, 0, 0, 0, 0, 0, 0],
             [0, 6, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 3, 0]]
        with self.assertRaises(solver.InvalidPuzzle):
            solver.solve(l)

    def test_sparse_board(self):
        """Will require many steps in DFS"""
        l = [[0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 1, 0, 0, 0, 0, 0, 0, 0],
             [0, 2, 0, 0, 0, 0, 0, 0, 0],
             [0, 4, 0, 0, 0, 0, 0, 0, 0],
             [0, 9, 0, 0, 0, 0, 0, 0, 0],
             [0, 7, 0, 0, 0, 0, 0, 3, 0],
             [0, 5, 0, 0, 0, 0, 0, 0, 0],
             [0, 6, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0]]
        sol = solver.solve(l)
        self.assertTrue(solver.is_valid(sol), sol)


class TestGenerate(TestCase):
    def test_generate(self):
        for difficulty in Difficulty:
            puzzle, sol = g.generate(difficulty, max_retries=50)
            self.assertTrue(solver.is_valid(puzzle), sol)
            self.assertTrue(solver.is_valid(sol), sol)

    def test_generate_max_retries(self):
        with self.assertRaises(MaxRetriesExceeded):
            g.generate(max_retries=0)


class TestTransform(TestCase):
    def setUp(self):
        self.puzzle = [[0, 0, 0, 0, 0, 0, 0, 1, 2],
                       [0, 0, 0, 0, 3, 5, 0, 0, 0],
                       [0, 0, 0, 6, 0, 0, 0, 7, 0],
                       [7, 0, 0, 0, 0, 0, 3, 0, 0],
                       [0, 0, 0, 4, 0, 0, 8, 0, 0],
                       [1, 0, 0, 0, 0, 0, 0, 0, 0],
                       [0, 0, 0, 1, 2, 0, 0, 0, 0],
                       [0, 8, 0, 0, 0, 0, 0, 4, 0],
                       [0, 5, 0, 0, 0, 0, 6, 0, 0]]

    def test_row_translate(self):
        t1 = g.row_translate(self.puzzle)

        self.assertEqual(
            t1,
            [[7, 0, 0, 0, 0, 0, 3, 0, 0],
             [0, 0, 0, 4, 0, 0, 8, 0, 0],
             [1, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 1, 2, 0, 0, 0, 0],
             [0, 8, 0, 0, 0, 0, 0, 4, 0],
             [0, 5, 0, 0, 0, 0, 6, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 1, 2],
             [0, 0, 0, 0, 3, 5, 0, 0, 0],
             [0, 0, 0, 6, 0, 0, 0, 7, 0]]
        )

        t11 = g.row_translate(t1)
        t2 = g.row_translate(self.puzzle, times=2)
        self.assertEqual(t11, t2)

        t111 = g.row_translate(t11)
        self.assertEqual(t111, self.puzzle)

