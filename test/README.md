## pytest

Our recommended way to run tests is through [pytest](https://docs.pytest.org/en/latest/).

Installation with your favorite package manager:

```
pip install -U pytest # pip

conda install pytest # conda
```

## Run Tests

To run the entire test suite, simply:

```
cd test
pytest 
```

To test a specific module:

```
pytest <test_module>.py
```

To learn more about how pytest detects tests, follow this [link](https://docs.pytest.org/en/latest/goodpractices.html#goodpractices).