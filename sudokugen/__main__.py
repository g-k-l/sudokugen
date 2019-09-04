import sys
from .client import client


if __name__ == "__main__":
    try:
        sys.argv[1]
    except IndexError:
        print('Valid options are "play", "solve", "gen" and "genmany"')
        sys.exit(0)

    if sys.argv[1] == "play":
        sys.exit(client() or 0)
