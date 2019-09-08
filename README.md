# Sudokugen

Package for solving and generating sudoku puzzles!

## Setup
```
pip install sudokugen
```

or

```
git clone https://github.com/g-k-l/sudoku-gen.git
cd sudoku-gen
pip install .
```


## Usage

### Solver

```python
>>> from sudokugen.solver import solve

>>> my_puzzle = [[0, 3, 6, 8, 9, 2, 7, 1, 5],
                 [5, 0, 2, 0, 7, 1, 9, 0, 3],
                 [9, 0, 7, 5, 6, 3, 4, 8, 2],
                 [0, 4, 3, 1, 5, 8, 2, 0, 7],
                 [8, 5, 9, 6, 0, 7, 1, 3, 0],
                 [7, 2, 0, 9, 3, 4, 8, 5, 6],
                 [0, 0, 0, 2, 8, 6, 5, 0, 1],
                 [0, 0, 0, 3, 1, 0, 0, 4, 9],
                 [0, 0, 0, 7, 4, 9, 3, 2, 8]]

>>> solution = solve(my_puzzle)
```

And solution looks like:
```
[[4, 3, 6, 8, 9, 2, 7, 1, 5],
 [5, 8, 2, 4, 7, 1, 9, 6, 3],
 [9, 1, 7, 5, 6, 3, 4, 8, 2],
 [6, 4, 3, 1, 5, 8, 2, 9, 7],
 [8, 5, 9, 6, 2, 7, 1, 3, 4],
 [7, 2, 1, 9, 3, 4, 8, 5, 6],
 [3, 9, 4, 2, 8, 6, 5, 7, 1],
 [2, 7, 8, 3, 1, 5, 6, 4, 9],
 [1, 6, 5, 7, 4, 9, 3, 2, 8]]
```

### Puzzle Generator

```python
from sudokugen.generator import generate, Difficulty


new_puzzle = generate(difficulty=Difficulty.MEDIUM)
```

Difficulty refers to the number of cells which have values assigned in the beginning. For `MEDIUM`, this number is `24`.
