# README #

### Running Dragons of Mugloar ###

If Docker is installed, then simply run with the count provided from command line:

```./script/server 1000```

If Docker is not installed, install requirements for Python:

```pip install -r requirements.txt```

And run python script directly:

```python dragons.py 1000```

Log file is created in the repo root: dragons.log

Current approx. battle success ratio: 92%

Known defeats happening when knight stats are 8444, 8543.


### Running tests ###

If Docker is installed, then simply run from command line:

```./script/test```

If Docker is not installed, run tests directly:

```py.test --cov-report html --cov=dragons -s -v test.py```

HTML coverage report is generated in htmlcov/index.html
