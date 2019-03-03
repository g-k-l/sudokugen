# Sudokugen

`sudokugen` contains:
- A Sudoku Solver
- A Sudoku Puzzle Generator
- Pipeline for creating large number of puzzles
- Curses Game Client

## Solver

Here is how to solve a given Sudoku puzzle using `sudokugen`:
```
my_puzzle="800003007600400358100080694904138506500200980280509040000300109369051070702946030"

python -m sudokugen solve $my_puzzle

[[ 8.  4.  5.  6.  9.  3.  2.  1.  7.]
 [ 6.  9.  7.  4.  1.  2.  3.  5.  8.]
 [ 1.  2.  3.  7.  8.  5.  6.  9.  4.]
 [ 9.  7.  4.  1.  3.  8.  5.  2.  6.]
 [ 5.  3.  6.  2.  7.  4.  9.  8.  1.]
 [ 2.  8.  1.  5.  6.  9.  7.  4.  3.]
 [ 4.  5.  8.  3.  2.  7.  1.  6.  9.]
 [ 3.  6.  9.  8.  5.  1.  4.  7.  2.]
 [ 7.  1.  2.  9.  4.  6.  8.  3.  5.]]
```
The contents of `my_puzzle` is a sequence of characters of length 81, the *flattened* version of a sudoku board via row traversal. `0` in `my_puzzle` indicates an empty cell.


## Puzzle Generator

You can also generate a arbitarily puzzle as follows:
```
python -m sudokugen gen

[[ 5.  6.  1.  4.  0.  0.  7.  9.  0.]
 [ 2.  3.  8.  0.  9.  7.  4.  6.  5.]
 [ 9.  0.  7.  5.  6.  3.  1.  8.  0.]
 [ 3.  1.  0.  9.  7.  4.  0.  0.  8.]
 [ 7.  5.  9.  3.  8.  2.  0.  1.  4.]
 [ 4.  0.  2.  0.  1.  0.  3.  7.  0.]
 [ 8.  0.  5.  7.  3.  6.  2.  0.  1.]
 [ 1.  7.  0.  2.  5.  9.  8.  3.  6.]
 [ 0.  2.  0.  8.  4.  0.  9.  0.  7.]]
 ```



## Puzzle Pipeline
`sudokugen` can be used to generate a large number of puzzles. The packages connects to a postgres server via `PG_CONN` and create a database of name `SUDOKU_DB_NAME` to store the generated puzzles and solutions.
```
export PG_CONN="postgres://..."
export SUDOKU_DB_NAME="my_sudoku_db"

python -m sudokugen genmany [n_jobs]
```
Here, `n_jobs` is the number of puzzle and solution pairs to generate. If omitted, the process will continue to generate puzzles and solutions until terminated.


## Game Client
There is also a `curses`-based interactive client which serves a randomly generated puzzle. Note, connection to a postgres database that contains generated puzzles and solutions is required.
```
export PG_CONN="postgres://..."
export SUDOKU_DB_NAME="my_sudoku_db"

python -m sudokugen play
```


