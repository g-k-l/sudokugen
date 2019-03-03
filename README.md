# Sudoku


## Solver

The contents of `my_puzzle` is a sequence of characters of length 81. Assume row traversal.
0 indicates an empty cell.
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


## Puzzle Generator
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


## Game Client
There is also a `curses`-based interactive client which serves a randomly generated puzzle.
```
python -m sudokugen play
```


