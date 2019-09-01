"""
This is a curses interface for the sudoku
game which can be accessed by providing "play"
as the first argument to __main__.py.
"""
import sys, os
import curses
import curses.ascii
from itertools import cycle, chain

import psycopg2

from .db import get_conn, get_puzzle


def grid_setup(height, width):
    cell_width = width // 10
    cell_height = height // 10
    return cell_height, cell_width


def coordinates(cell_height, cell_width):
    cell_corners, cell_centers = [], []
    for n in range(9):
        for j in range(9):
            cell_corners.append((
                1 + cell_height*n, 1 + cell_width*j,))
            cell_centers.append((
                1 + cell_height*n + cell_height//2,
                1 + cell_width*j + cell_width//2,))
    return cell_corners, cell_centers


def adjust_cursor(cursor_y, cursor_x, cell_centers):
    dists = [abs(cursor_y - cell_y) + abs(cursor_x - cell_x)
        for (cell_y, cell_x) in cell_centers]
    return cell_centers[dists.index(min(dists))]


def draw_menu(stdscr):
    k = 0
    cursor_x = 1
    cursor_y = 1

    conn = get_conn()
    puzzle, sol = get_puzzle(conn.cursor())
    solution = list(chain.from_iterable(sol))
    orig_puzzle = list(chain.from_iterable(puzzle))
    puzzle = [c if c != '0' else '' for c in orig_puzzle]

    # Clear and refresh the screen for a blank canvas
    stdscr.clear()
    stdscr.refresh()

    # Start colors in curses
    curses.start_color()
    curses.init_color(8, 0, 0, 0)
    curses.init_color(9, 105, 105, 105)
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_RED)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)

    # Loop where k is the last character pressed
    while k != ord('q'):

        # Initialization
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        cell_height, cell_width = grid_setup(height, width)
        cell_corners, cell_centers = coordinates(cell_height, cell_width)

        status_msg = "Press 'Enter' to check, 'q' to exit"
        if k == curses.KEY_DOWN:
            cursor_y = cursor_y + cell_height
        elif k == curses.KEY_UP:
            cursor_y = cursor_y - cell_height
        elif k == curses.KEY_RIGHT:
            cursor_x = cursor_x + cell_width
        elif k == curses.KEY_LEFT:
            cursor_x = cursor_x - cell_width
        elif curses.ascii.isdigit(k) and k != ord('0'):
            idx = cell_centers.index((cursor_y, cursor_x))
            if orig_puzzle[idx] != "0":
                status_msg = 'Cannot update cell with existing value.'
            else:
                status_msg = 'Updated cell value to {}.'.format(chr(k))
                puzzle[idx] = chr(k)
        elif k in (curses.ascii.DEL, curses.ascii.BS):
            idx = cell_centers.index((cursor_y, cursor_x))
            if orig_puzzle[idx] != "0":
                status_msg = 'Cannot update cell with existing value.'
            else:
                status_msg = 'Removed cell value.'
                puzzle[idx] = ""
        elif k == curses.ascii.LF:
            if puzzle == solution:
                status_msg = 'You have solved the puzzle!'
            else:
                status_msg = 'Submission incorrect.'

        cycle_colors = cycle([curses.color_pair(2), curses.color_pair(3)])
        empty_space_padding = " "*(cell_width)
        for cell_y, cell_x in cell_corners:
            color_pair = next(cycle_colors)
            stdscr.attron(color_pair)
            for n in range(cell_height):
                stdscr.addstr(cell_y + n, cell_x, empty_space_padding)
            stdscr.attroff(color_pair)

        next(cycle_colors)
        stdscr.attron(curses.A_BOLD)
        for cell_val, (cell_y, cell_x) in zip(puzzle, cell_centers):
            color_pair = next(cycle_colors)
            stdscr.attron(color_pair)
            stdscr.addstr(cell_y, cell_x, cell_val)
            stdscr.attroff(color_pair)
        stdscr.attroff(curses.A_BOLD)

        cursor_y, cursor_x = adjust_cursor(cursor_y, cursor_x, cell_centers)

        # Declaration of strings
        statusbarstr = " {} | Pos: {}, {}".format(
            status_msg, cursor_x, cursor_y)[:width-1]

        # Render status bar
        stdscr.attron(curses.color_pair(3))
        stdscr.addstr(height-1, 0, statusbarstr)
        stdscr.addstr(height-1, len(statusbarstr), " " * (width - len(statusbarstr) - 1))
        stdscr.attroff(curses.color_pair(3))

        stdscr.move(cursor_y, cursor_x)

        # # Refresh the screen
        stdscr.refresh()

        # # Wait for next input
        k = stdscr.getch()


def client():
    curses.wrapper(draw_menu)
