import sys

from .gen_sol import main
from .client import client

if __name__ == "__main__":
    if sys.argv[1] == "play":
        sys.exit(client() or 0)     
    else:
        try:
            n_jobs = int(sys.argv[1])
        except (IndexError, ValueError):
            n_jobs = None 
        sys.exit(main(n_jobs) or 0)
