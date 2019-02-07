from setuptools import setup

setup(name='sudokugen',
      version='0.1',
      description='Sudoku!',
      url='http://github.com/g-k-l/sudoku-gen',
      author='Kevin Liu',
      author_email='kevin.g.k.liu@gmail.com',
      license='MIT',
      packages=['sudokugen'],
      zip_safe=False,
      classifiers=[
        "Sudoku Solver", "Sudoku Generator",
        "backtracking",
      ],)
