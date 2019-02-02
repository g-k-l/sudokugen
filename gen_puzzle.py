
from concurrent.futures import ProcessPoolExecutor
import sqlite3

import numpy as np


def from_db(conn, limit=10):
    c = conn.cursor()
    if limit:
        c.execute("SELECT * FROM solutions LIMIT {};".format(limit))
    else:
        c.execute("SELECT * FROM solutions;")
    return [np.array(row).reshape((9, 9)) for row in c.fetchall()]

