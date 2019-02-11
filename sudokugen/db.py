
import asyncio
import os

import asyncpg


DB_NAME = "sudoku"
PG_SERVER = "postgres://localhost:5432/"
DB_CONN = os.path.join(PG_SERVER, DB_NAME)


async def setup_db(conn):
    db = """CREATE DATABASE {};""".format(DB_NAME)

    solution = """
        CREATE TABLE IF NOT EXISTS solution (
            id SERIAL PRIMARY KEY,
            board INTEGER
        );
    """

    puzzle = """
        CREATE TABLE IF NOT EXISTS puzzle (
            id SERIAL PRIMARY KEY,
            board INTEGER,
            sol_id INTEGER REFERENCES solution(id)
        );
    """
    try:
        await conn.execute(db)
    except asyncpg.DuplicateDatabaseError:
        print("Database already exists.")
    else:
        print("Created {}".format(DB_NAME))


    db_conn = await asyncpg.connect(DB_CONN)
    await db_conn.execute(solution)
    print("Created solution table.")

    await db_conn.execute(puzzle)
    print("Created puzzle table.")


async def insert_solutions(boards, conn):
    insert = """
        INSERT INTO solution (board) VALUES {};
    """
    rows = ",\n".join([
        "({})".format("".join(board.flatten()))
        for board in boards])
    await conn.execute(insert.format(rows))


async def insert_puzzles(boards_and_sol_ids, conn):
    insert = """
        INSERT INTO puzzles (board, sol_id) VALUES {};
    """
    rows = ",\n".join(["({}, {})".format(board.flatten(), sol_id)
        for board, sol_id in boards_and_sol_ids])
    await conn.execute(insert.format(rows))


async def get_conn(conn_str=DB_CONN):
    return await asyncpg.connect(conn_str)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    conn = loop.run_until_complete(get_conn())
    loop.run_until_complete(setup_db(conn))
