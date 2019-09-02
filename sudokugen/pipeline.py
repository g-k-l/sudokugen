from collections import defaultdict
from copy import copy
from dataclasses import dataclass
import heapq
import multiprocessing as mp
from multiprocessing.managers import BaseManager
from queue import LifoQueue
import random
import time

EMPTY = 0
DIM = 9
SIZE = 81

import numpy as np

def empty_puzzle():
    """Returns an tuple of 81 zeros"""
    return [EMPTY for __ in range(SIZE)]


def block_indices():
    blocks = defaultdict(set)
    for k in range(SIZE):
        r, c = (k // DIM), (k % DIM)
        b = (r // 3) + 3*(c // 3)
        blocks[b].add(k)
    # remove the default property
    return dict(blocks)


def indices():
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


"""
puzzle and board are each 9x9 numpy matrix,
pencil_marks is a dict with matrix indices as keys
and the possible values for those index
locations in the sudoku puzzle.
"""

@dataclass(order=True, frozen=True)
class CellCandidates:
    cell: int
    priority: int
    candidates: set


class SudokuWorker(mp.Process):
    """
    A process whose task is to take the next item
    off the stack and process it.
    """
    def __init__(self, stack, visited, solset):
        """stack is an instance of queue.LifoQueue
            visited and solset are each sets"""
        super().__init__(daemon=True)
        self.stack = stack
        self.visited = visited
        self.solset = solset

    # @staticmethod
    # def puzzle_str(puzzle):
    #     s = ""
    #     for k in range(len(SIZE)):


    @staticmethod
    def rand_empty_cell(puzzle):
        emptys = [k for k, v in enumerate(puzzle) if v == EMPTY]
        return random.choice(emptys)

    @staticmethod
    def get_candidates(puzzle):
        """
        Build a list of possible values for each
        cell in the puzzle. Prioritize returning
        cells which have only one possible value.
        If there is no such cell, then take a guess.
        """
        all_cands = []
        for k, cell in enumerate(puzzle):
            if cell != EMPTY:
                continue

            r, c = (k // DIM), (k % DIM)
            b = (r // 3) + 3*(c // 3)

            cands = {n+1 for n in range(DIM)}
            for l in ROW_INDICES[r]:
                cands.discard(puzzle[l])
            for m in COL_INDICES[c]:
                cands.discard(puzzle[m])
            for n in BLOCK_INDICES[b]:
                cands.discard(puzzle[n])
            if len(cands) == 0:
                # puzzle contains a cell that has no candidate
                # so the puzzle is unsolvable
                return None

            cands_obj = CellCandidates(
                cell=k, priority=len(cands), candidates=cands)

            heapq.heappush(all_cands, cands_obj)

        return all_cands

    def run(self):
        stack, visited = self.stack, self.visited
        while True:
            if stack.empty():
                time.sleep(0.1)

            puzzle = stack.get()
            visited.add(tuple(puzzle))
            print(np.array(puzzle).reshape(9,9))

            all_cands = self.get_candidates(puzzle)
            if all_cands == {}:
                # puzzle is completely filled - solved
                print("=====Solved====")
                print(np.array(puzzle).reshape(9,9))
                self.solset.add(tuple(puzzle))
            elif all_cands is None:
                # at least one cell has no candidate,
                # so the puzzle is unsolvable
                continue
            else:
                min_constraint = all_cands[0].priority
                while all_cands:
                    cands_obj = heapq.heappop(all_cands)
                    if cands_obj.priority > min_constraint:
                        break
                    for cand in cands_obj.cands:
                        next_puzzle = copy(puzzle)
                        next_puzzle[cand.cell] = cand
                        if tuple(next_puzzle) not in visited:
                            stack.put(next_puzzle)


                # deterministic = {
                #     k: list(v)[0] for k, v in all_cands.items() if len(v) == 1}
                # if deterministic:
                #     for k, v in deterministic.items():
                #         next_puzzle = copy(puzzle)
                #         next_puzzle[k] = v
                #         if tuple(next_puzzle) not in visited:
                #             stack.put(next_puzzle)
                # else:
                #     rand = random.choice(list(all_cands.keys()))
                #     for v in all_cands[rand]:
                #         next_puzzle = copy(puzzle)
                #         next_puzzle[rand] = v
                #         if tuple(next_puzzle) not in visited:
                #             stack.put(next_puzzle)



class SudokuManager(BaseManager):
    """
    Manages data shared amongst processes by
    producing producing proxy objects
    """


SudokuManager.register('set', set)
SudokuManager.register('LifoQueue', LifoQueue)


def main_single():
    stack = LifoQueue()
    visited, solset = set(), set()

    # from itertools import chain
    # puzzle = list(chain(
    #    [0, 3, 6, 8, 9, 2, 7, 1, 5],
    #    [5, 0, 2, 0, 7, 1, 9, 0, 3],
    #    [9, 0, 7, 5, 6, 3, 4, 8, 2],
    #    [0, 4, 3, 1, 5, 8, 2, 0, 7],
    #    [8, 5, 9, 6, 0, 7, 1, 3, 0],
    #    [7, 2, 0, 9, 3, 4, 8, 5, 6],
    #    [0, 0, 0, 2, 8, 6, 5, 0, 1],
    #    [0, 0, 0, 3, 1, 0, 0, 4, 9],
    #    [0, 0, 0, 7, 4, 9, 3, 2, 8]))

    # stack.put(puzzle)
    stack.put(empty_puzzle())
    worker = SudokuWorker(stack, visited, solset)
    worker.run()


# m = SudokuManager()
# visited = m.set()
# stack = m.LifoQueue()
# solset = m.set()

# nprocs = 16
# procs = [SudokuWorker() for __ in range(nprocs)]
