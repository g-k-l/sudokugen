from itertools import islice
import os

import psycopg2


DB_NAME = os.environ.get("SUDOKU_DB_NAME", "sudoku")
PG_SERVER = os.environ.get("PG_CONN", "postgres://localhost:5432/")
DB_CONN = os.path.join(PG_SERVER, DB_NAME)


def setup_db():
    db = """CREATE DATABASE {};""".format(DB_NAME)

    solution = """
        CREATE TABLE IF NOT EXISTS solution (
            board VARCHAR(81) PRIMARY KEY
        );
    """
    puzzle = """
        CREATE TABLE IF NOT EXISTS puzzle (
            id SERIAL PRIMARY KEY,
            board VARCHAR(81),
            sol VARCHAR(81) REFERENCES solution(board)
        );
    """
    conn = psycopg2.connect(PG_SERVER)
    conn.autocommit = True
    try:
        conn.cursor().execute(db)
    except psycopg2.ProgrammingError:
        print("Database already exists.")
    else:
        print("Created {}".format(DB_NAME))


    conn = psycopg2.connect(DB_CONN)
    conn.autocommit = True
    cursor = conn.cursor()
    cursor.execute(solution)
    print("Created solution table.")

    cursor.execute(puzzle)
    print("Created puzzle table.")


def to_strings(board):
    return [str(n) for n in board.flatten()]


def insert_solutions(boards, cursor):
    insert = """
        INSERT INTO solution (board) VALUES {};
    """
    as_values_query = ["('{}')".format(board_str) 
        for board_str in uniques_only(boards, cursor)]
    rows = ",\n".join(as_values_query)
    cursor.execute(insert.format(rows))


def insert_puzzles(boards_and_sols, cursor):
    insert = """
        INSERT INTO puzzle (board, sol) VALUES {};
    """
    rows = ",\n".join(["({}, {})".format(
        ''.join(to_strings(board)), ''.join(to_strings(sol)))
        for board, sol in boards_and_sols])
    cursor.execute(insert.format(rows))


def uniques_only(boards, cursor):
    template = """
        SELECT board FROM solution WHERE board IN ('{}');
    """
    board_strs = {"".join(to_strings(board)) for board in boards}
    maybe_dups = ", ".join(board_strs)
    dups = cursor.execute(template.format(maybe_dups))
    if not dups:
        return board_strs
    return board_strs - set(dups)


def get_puzzle(cursor, puzzle_id=None):
    if puzzle_id is None:
        stmt = """
            SELECT board, sol FROM puzzle ORDER BY RANDOM() LIMIT 1;
        """
    else:
        stmt = """
            SELECT board, sol from puzzle WHERE id = {};
        """.format(puzzle_id)
    cursor.execute(stmt)
    board_str, sol_str = cursor.fetchone()
    board = [list(islice(board_str, 9*n, 9*(n+1))) for n in range(9)]
    sol = [list(islice(sol_str, 9*k, 9*(k+1))) for k in range(9)]
    return board, sol


def get_conn(conn_str=DB_CONN):
    return psycopg2.connect(conn_str)


if __name__ == "__main__":
    setup_db()
