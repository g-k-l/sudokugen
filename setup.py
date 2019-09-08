from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()


setup(name='sudokugen',
      python_requires=">=3.6.9",
      version='0.2.1',
      description='A sudoku puzzle solver and generator',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='http://github.com/g-k-l/sudokugen',
      author='Kevin Liu',
      author_email='kevin.g.k.liu@gmail.com',
      license='GNUPL',
      packages=find_packages(),
      zip_safe=True,
      )
