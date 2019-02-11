import sys

from .gen_sol import main

if __name__ == "__main__":
    try:
        n_jobs = int(sys.argv[1])
    except (IndexError, ValueError):
        n_jobs = None 

    sys.exit(main(n_jobs) or 0)
