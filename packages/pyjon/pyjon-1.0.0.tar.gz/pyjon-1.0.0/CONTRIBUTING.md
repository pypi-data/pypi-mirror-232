# CONTRIBUTING

This file contains basic guidelines to help developers contribute on this project.


## Installation

As this package does not rely on any external packages, you just need to clone this repository to start working on it:

```bash
git clone https://github.com/just1not2/pyjon.git
cd pyjon
```

It is recommended to work in a Python virtual environment:

```bash
make env
```


## Test

Once you developed a feature or a fix, the best way to try it is to launch the tests available in the `tests/` directory:

```bash
make test
```

Note that these tests should be updated whenever a big feature is added to the repository in order to cover the largest portion of code possible.


## Linter

Pylint is currently the only tool used on the repository to ensure a good code quality. Please resolve all warnings that are returned before opening a PR:

```bash
make lint
```
