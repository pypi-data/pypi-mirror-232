# Overview

**THIS PLUGIN IS IN DEVELOPMENT -- Expect bugs. Expect incomplete behaviour**

`pytest-maxcov` is a [pytest](https://pypi.org/project/pytest/) plugin to compute the maximum coverage available through pytest with the minimum execution time cost. The plugin serves two main use cases:

* to identify redundant unit tests which do not add additional coverage
* to discover a subset of unit tests which achieves a minimum coverage level, for example to create a fast subset for a smoke test

[![PyPI version](https://badge.fury.io/py/pytest-maxcov.svg)](https://badge.fury.io/py/pytest-maxcov)

## Installation

``` bash
python3 -m pip install pytest-maxcov
```

## Usage

The plugin works in two passes:

1. Run alongside `pytest-cov` to collect coverage information and time every test. Pass `--maxcov-record` on the command-line to `pytest` to configure the plugin to capture the data it needs for the second pass. You must also include `--cov-context=text` to that per-test coverage can be measured.
2. Run using `--maxcov` to read the data from pass one to mark tests as skipped if they are not needed to achieve the chosen coverage level.

The command-line option `--maxcov-threshold` specifies the threshold for computing the minimum set of tests. By default this is 100%.

For example using Poetry and [pytest-xdist](https://pypi.org/project/pytest-xdist/):

``` text
poetry run pytest -n logical --maxcov-record --cov=mypackage --cov-branch --cov-context=test
poetry run pytest -n logical --maxcov --cov=mypackage --cov-branch
```

## Limitations

Current limitations include:

* multiple contexts are not supported; the plugin assumes everything runs in a single context
* multiple coverage files are not supported; the plugin reads from `.coverage` by default or the data file specified by the environment variable `COVERAGE_FILE`

## License

All code in this repository is licensed under the [MIT License](https://github.com/masaccio/pytest-maxcov/blob/master/LICENSE)
