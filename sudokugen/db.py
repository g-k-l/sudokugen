import os

import psycopg2


DB_NAME = "sudoku"
PG_SERVER = "postgres://localhost:5432/"
DB_CONN = os.path.join(PG_SERVER, DB_NAME)


def setup_db():
    db = """CREATE DATABASE {};""".format(DB_NAME)

    solution = """
        CREATE TABLE IF NOT EXISTS solution (
            board INTEGER PRIMARY KEY
        );
    """
    puzzle = """
        CREATE TABLE IF NOT EXISTS puzzle (
            id SERIAL PRIMARY KEY,
            board INTEGER,
            sol INTEGER REFERENCES solution(board)
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


def insert_solutions(boards, cursor):
    insert = """
        INSERT INTO solution (board) VALUES {};
    """
    row_vals = uniques_only(boards, cursor)
    rows = "\n".join(row_vals)
    cursor.execute(insert.format(rows))


def insert_puzzles(boards_and_sols, cursor):
    insert = """
        INSERT INTO puzzles (board, sol) VALUES {};
    """
    rows = ",\n".join(["({}, {})".format(board.flatten(), sol.flatten())
        for board, sol in boards_and_sols])
    cursor.execute(insert.format(rows))


def uniques_only(boards, cursor):
    template = """
        SELECT board FROM solution WHERE board IN ('{}');
    """
    board_strs = {"".join(board.flatten()) for board in boards}
    maybe_dups = ", ".join(board_strs)
    dups = set(cursor.execute(template.format(maybe_dups)))
    return board_strs - dups


def get_conn(conn_str=DB_CONN):
    return psycopg2.connect(conn_str)


if __name__ == "__main__":
    setup_db()
